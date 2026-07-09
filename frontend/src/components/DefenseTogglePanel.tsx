import { Card, SimpleGrid, Switch, Title } from '@mantine/core';
import type { DefenseProfile } from '../types';

const labels: Array<[keyof DefenseProfile, string]> = [
  ['inputModeration', '输入检测'],
  ['promptInjectionDetection', '提示注入检测'],
  ['encodingNormalization', '编码规范化'],
  ['instructionDataSeparation', '指令/数据隔离'],
  ['outputModeration', '输出检测'],
  ['toolPolicyEnforcement', '工具策略'],
  ['humanConfirmationRequired', '人工确认'],
  ['rateLimit', '限流'],
];

export default function DefenseTogglePanel({ value, onChange }: { value: DefenseProfile; onChange: (value: DefenseProfile) => void }) {
  return (
    <Card withBorder radius="md">
      <Title order={4} mb="md">防御开关</Title>
      <SimpleGrid cols={{ base: 1, sm: 2 }}>
        {labels.map(([key, label]) => (
          <Switch
            key={key}
            checked={value[key]}
            label={label}
            onChange={(event) => onChange({ ...value, [key]: event.currentTarget.checked })}
          />
        ))}
      </SimpleGrid>
    </Card>
  );
}
