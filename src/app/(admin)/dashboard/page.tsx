import { Form } from "@/app/components/Form";
import { StatsGrid } from "@/app/components/StatsGrid";
import { Flex, Space, Title } from "@mantine/core";

export default function Dashboard() {
  return (
    <div className="p-6">
      <Title order={3}>Dashboard</Title>
      <Space h="lg" />
      <StatsGrid />
      <Space h="lg" />
      <Flex
        mih={50}
        gap="md"
        justify="center"
        align="center"
        direction="row"
        wrap="wrap"
      >
        <Form />
        <div className="flex-1 guide h-28"></div>
      </Flex>
    </div>
  );
}
