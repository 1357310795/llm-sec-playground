import { Badge, Card, Stack, Table, Text, Title } from '@mantine/core';
import type { RiskEvent } from '../types';

const severityColor: Record<RiskEvent['severity'], string> = {
  low: 'gray',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
};

export default function RiskEventList({ events }: { events: RiskEvent[] }) {
  return (
    <Card withBorder radius="md">
      <Stack>
        <Title order={4}>风险事件</Title>
        {events.length === 0 ? <Text c="dimmed">未记录风险事件。</Text> : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>级别</Table.Th>
                <Table.Th>来源</Table.Th>
                <Table.Th>类型</Table.Th>
                <Table.Th>处置</Table.Th>
                <Table.Th>说明</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {events.map((event, index) => (
                <Table.Tr key={`${event.type}-${index}`}>
                  <Table.Td><Badge color={severityColor[event.severity]}>{event.severity}</Badge></Table.Td>
                  <Table.Td>{event.source}</Table.Td>
                  <Table.Td>{event.type}</Table.Td>
                  <Table.Td>{event.action}</Table.Td>
                  <Table.Td>{event.message}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Stack>
    </Card>
  );
}
