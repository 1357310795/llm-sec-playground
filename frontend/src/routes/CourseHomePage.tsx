import { Alert, SimpleGrid, Skeleton, Stack, Text, Title } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import { getScenarios } from '../api/scenarios';
import ScenarioCard from '../components/ScenarioCard';

export default function CourseHomePage() {
  const { data, isLoading, error } = useQuery({ queryKey: ['scenarios'], queryFn: getScenarios });

  return (
    <Stack>
      <Title>课程首页</Title>
      <Text c="dimmed">基于参考文档构建的授权教学靶场：角色扮演、指令操纵、编码混淆、RAG 注入、恶意 Schema、Agent 工具滥用。</Text>
      <Alert color="blue" title="安全说明">所有训练目标均为无害 flag、假文档、假用户和模拟工具调用；不会执行真实外部动作。</Alert>
      {error && <Alert color="red">加载失败：{(error as Error).message}</Alert>}
      {isLoading ? <Skeleton height={220} /> : (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }}>
          {(data ?? []).map((scenario) => <ScenarioCard key={scenario.id} scenario={scenario} />)}
        </SimpleGrid>
      )}
    </Stack>
  );
}
