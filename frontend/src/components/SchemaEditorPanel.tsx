import { Textarea } from '@mantine/core';

export const DEFAULT_SCHEMA_TEXT = `{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["ok", "CDA_TRAINING_FLAG"]
    }
  }
}`;

export default function SchemaEditorPanel({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <Textarea
      label="JSON Schema"
      description="Schema 本身也是训练攻击面：description、enum、default、pattern 都会被分析。"
      rows={16}
      value={value}
      onChange={(event) => onChange(event.currentTarget.value)}
      styles={{ input: { fontFamily: 'monospace', resize: 'vertical' } }}
    />
  );
}
