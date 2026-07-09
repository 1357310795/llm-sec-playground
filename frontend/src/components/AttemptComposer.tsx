import { Button, Card, Stack, Textarea, Title } from '@mantine/core';
import type { Scenario } from '../types';
import RagDocumentPanel from './RagDocumentPanel';
import SchemaEditorPanel from './SchemaEditorPanel';

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
  return (
    <Card withBorder radius="md">
      <Stack>
        <Title order={4}>提交训练尝试</Title>
        {scenario.allowedInputs.includes('chat') && (
          <Textarea
            label="用户提示"
            minRows={5}
            value={message}
            onChange={(event) => onMessageChange(event.currentTarget.value)}
            placeholder="输入无害训练尝试，例如观察角色边界、指令优先级或模拟工具行为"
          />
        )}
        {scenario.allowedInputs.includes('file') && <RagDocumentPanel value={documentText} onChange={onDocumentTextChange} />}
        {scenario.allowedInputs.includes('schema') && <SchemaEditorPanel value={schemaText} onChange={onSchemaTextChange} />}
        <Button onClick={onSubmit} loading={loading}>提交并运行沙盒链路</Button>
      </Stack>
    </Card>
  );
}
