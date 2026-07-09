import { Alert, Badge, Card, Group, Skeleton, Stack, Text, Title } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { getReplay } from '../api/scenarios';
import ReplayTimeline from '../components/ReplayTimeline';
import RiskEventList from '../components/RiskEventList';

export default function ReplayPage() {
  const { attemptId = '' } = useParams();
  const { data, isLoading, error } = useQuery({ queryKey: ['replay', attemptId], queryFn: () => getReplay(attemptId), enabled: Boolean(attemptId) });

  if (isLoading) return <Skeleton height={400} />;
  if (error) return <Alert color="red">加载失败：{(error as Error).message}</Alert>;
  if (!data) return <Alert color="red">复盘不存在。</Alert>;

  return (
    <Stack>
      <Group justify="space-between">
        <Title>复盘页</Title>
        <Badge size="lg">得分 {data.score}</Badge>
      </Group>
      <ReplayTimeline timeline={data.timeline} />
      <RiskEventList events={data.riskEvents} />
      <Card withBorder radius="md">
        <Title order={4}>修复建议</Title>
        <Stack gap={6} mt="sm">
          {data.repairAdvice.map((item) => <Text key={item}>• {item}</Text>)}
        </Stack>
      </Card>
    </Stack>
  );
}
