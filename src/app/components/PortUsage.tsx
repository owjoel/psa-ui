import { Box, Flex, Paper, RingProgress, Text, Title } from "@mantine/core";

export default function PortUsage() {
  return (
    <Paper withBorder p="md" radius="md" h="100%" className="h-full w-64">
      <Flex direction="column" align="center" h={"100%"}>
        <Title order={2}>Berth Capacity</Title>
        <Box className="grow flex items-center">
          <RingProgress
            size={140}
            sections={[{ value: 60, color: "blue" }]}
            label={
              <Text c="blue" fw={700} ta="center" size="xl">
                60%
              </Text>
            }
          />
        </Box>
      </Flex>
    </Paper>
  );
}
