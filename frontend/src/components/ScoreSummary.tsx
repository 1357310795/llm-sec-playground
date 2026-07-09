import { Badge, Card, Group, Progress, Stack, Text, Title } from '@mantine/core';

export default function ScoreSummary({ score, status, safeOutput }: { score: number; status: string; safeOutput: string }) {
  return (
    <Card withBorder radius="md">
      <Stack>
        <Group justify="space-between">
          <Title order={4}>结果摘要</Title>
          <Badge>{status}</Badge>
        </Group>
        <Progress value={score} size="lg" />
        <Text fw={700}>得分：{score}</Text>
        <Text style={{ whiteSpace: 'pre-wrap' }}>{safeOutput}</Text>
      </Stack>
    </Card>
  );
}
