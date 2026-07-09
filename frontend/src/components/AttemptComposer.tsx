import { Button, Card, Group, Stack, Textarea, Title } from '@mantine/core';
import type { Scenario } from '../types';
import RagDocumentPanel from './RagDocumentPanel';
import SchemaEditorPanel from './SchemaEditorPanel';

function unicodeEncode(value: string) {
  return value.split('').map((char) => `\\u${char.charCodeAt(0).toString(16).padStart(4, '0')}`).join('');
}

function unicodeDecode(value: string) {
  return value.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex: string) => String.fromCharCode(Number.parseInt(hex, 16)));
}

function base64Encode(value: string) {
  const bytes = new TextEncoder().encode(value);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function base64Decode(value: string) {
  try {
    const binary = atob(value);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  } catch {
    return value;
  }
}

function rot13(value: string) {
  return value.replace(/[a-zA-Z]/g, (char) => {
    const base = char <= 'Z' ? 65 : 97;
    return String.fromCharCode(((char.charCodeAt(0) - base + 13) % 26) + base);
  });
}

export default function AttemptComposer({
  scenario,
  message,
  onMessageChange,
  schemaText,
  onSchemaTextChange,
  documentText,
  onDocumentTextChange,
  onSubmit,
  loading,
}: {
  scenario: Scenario;
  message: string;
  onMessageChange: (value: string) => void;
  schemaText: string;
  onSchemaTextChange: (value: string) => void;
  documentText: string;
  onDocumentTextChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}) {
  const showEncodingTools = scenario.id === 'encoding-obfuscation';

  return (
    <Card withBorder radius="md">
      <Stack>
        <Title order={4}>提交训练尝试</Title>
        {scenario.allowedInputs.includes('chat') && (
          <>
            <Textarea
              label="用户提示"
              minRows={5}
              value={message}
              onChange={(event) => onMessageChange(event.currentTarget.value)}
              placeholder="输入无害训练尝试，例如观察角色边界、指令优先级或模拟工具行为"
            />
            {showEncodingTools && (
              <Group gap="xs">
                <Button size="xs" variant="light" onClick={() => onMessageChange(unicodeEncode(message))}>Unicode 加密</Button>
                <Button size="xs" variant="light" onClick={() => onMessageChange(unicodeDecode(message))}>Unicode 解密</Button>
                <Button size="xs" variant="light" onClick={() => onMessageChange(base64Encode(message))}>Base64 加密</Button>
                <Button size="xs" variant="light" onClick={() => onMessageChange(base64Decode(message))}>Base64 解密</Button>
                <Button size="xs" variant="light" onClick={() => onMessageChange(rot13(message))}>ROT13 加密</Button>
                <Button size="xs" variant="light" onClick={() => onMessageChange(rot13(message))}>ROT13 解密</Button>
              </Group>
            )}
          </>
        )}
        {scenario.allowedInputs.includes('file') && <RagDocumentPanel value={documentText} onChange={onDocumentTextChange} />}
        {scenario.allowedInputs.includes('schema') && <SchemaEditorPanel value={schemaText} onChange={onSchemaTextChange} />}
        <Button onClick={onSubmit} loading={loading}>提交并运行沙盒链路</Button>
      </Stack>
    </Card>
  );
}
