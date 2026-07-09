import { Card, Code, Stack, Timeline, Title } from '@mantine/core';

export default function ReplayTimeline({ timeline }: { timeline: Array<Record<string, unknown>> }) {
  return (
    <Card withBorder radius="md">
      <Stack>
        <Title order={4}>沙盒链路复盘</Title>
        <Timeline active={timeline.length} bulletSize={24} lineWidth={2}>
          {timeline.map((item, index) => (
            <Timeline.Item key={index} title={String(item.phase ?? `phase-${index}`)}>
              <Code block>{JSON.stringify(item, null, 2)}</Code>
            </Timeline.Item>
          ))}
        </Timeline>
      </Stack>
    </Card>
  );
}
