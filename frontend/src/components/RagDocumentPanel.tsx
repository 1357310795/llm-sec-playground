import { Textarea } from '@mantine/core';

export default function RagDocumentPanel({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return (
    <Textarea
      label="临时 RAG 文档"
      description="内容只进入训练沙盒，不会访问真实网络或文件系统。"
      minRows={4}
      value={value}
      onChange={(event) => onChange(event.currentTarget.value)}
      placeholder="可放入包含 RAG_INJECTION_TRAINING_FLAG 的训练污染样本，观察隔离效果。"
    />
  );
}
