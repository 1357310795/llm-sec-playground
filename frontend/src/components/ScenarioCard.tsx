import { Badge, Button, Card, Group, Stack, Text, Title } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { Scenario } from '../types';

const colors = { easy: 'green', medium: 'yellow', hard: 'red' } as const;

export default function ScenarioCard({ scenario }: { scenario: Scenario }) {
  return (
    <Card withBorder shadow="sm" radius="md" h="100%">
      <Stack gap="sm" h="100%">
        <Group justify="space-between" align="start">
          <Title order={4}>{scenario.title}</Title>
          <Badge color={colors[scenario.difficulty]}>{scenario.difficulty}</Badge>
        </Group>
        <Text size="sm" c="dimmed">{scenario.summary}</Text>
        <Group gap={6}>
          {scenario.chapterRefs.map((chapter) => <Badge key={chapter} variant="light">章节 {chapter}</Badge>)}
        </Group>
        <Text size="sm">防御点：{scenario.learningGoals.slice(0, 3).join(' / ')}</Text>
        <Text size="xs" c="dimmed">训练目标：{scenario.trainingTargets.join(', ')}</Text>
        <Button component={Link} to={`/scenarios/${scenario.id}`} mt="auto">进入场景</Button>
      </Stack>
    </Card>
  );
}
