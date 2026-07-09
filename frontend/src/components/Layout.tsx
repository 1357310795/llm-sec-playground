import { AppShell, Container, Group, Text, Title } from '@mantine/core';
import { Link } from 'react-router-dom';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <AppShell header={{ height: 72 }} padding="md">
      <AppShell.Header>
        <Container size="xl" h="100%">
          <Group h="100%" justify="space-between">
            <Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}>
              <Title order={3}>LLM 安全攻防训练靶场</Title>
            </Link>
          </Group>
        </Container>
      </AppShell.Header>
      <AppShell.Main>
        <Container size="xl">{children}</Container>
      </AppShell.Main>
    </AppShell>
  );
}
