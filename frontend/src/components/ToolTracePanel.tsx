import { Card, Code, Stack, Text, Title } from '@mantine/core';

export default function ToolTracePanel({ calls }: { calls: Array<Record<string, unknown>> }) {
  return (
    <Card withBorder radius="md">
      <Stack>
        <Title order={4}>工具调用轨迹</Title>
        {calls.length === 0 ? <Text c="dimmed">本次没有模拟工具调用。</Text> : <Code block>{JSON.stringify(calls, null, 2)}</Code>}
      </Stack>
    </Card>
  );
}
