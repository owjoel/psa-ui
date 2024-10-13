import {
  Box,
  Button,
  Container,
  Divider,
  Flex,
  Paper,
  Space,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import classes from "./Form.module.css";
import { IconCrane } from "@tabler/icons-react";

export function Form() {
  return (
    <Paper withBorder p="md" radius="md"  h="40%"  className="flex-1 ">
      <Flex>
        <div className="grow">
          <Title order={6}>Recommended Berth</Title>
          <Space h="xs" />
          <Flex
            mih={5}
            gap="xs"
            justify="flex-start"
            align="flex-start"
            direction="column"
            wrap="wrap"
          >
            {/* <TextInput
              label="Shipping address"
              placeholder="15329 Huston 21st"
              classNames={classes}
            /> */}
          </Flex>
          <Space h="lg" />
          <Button rightSection={<IconCrane size={14} />}>Recompute Best Berth</Button>
        </div>
        <Divider orientation="vertical" />
        <Box w="60rem" pl={10}>
          <Text fz="xs" tt="uppercase" fw={700} c="dimmed">Assigned</Text>
          <Text fz="xl" fw={700}>B4</Text>
        </Box>
      </Flex>
    </Paper>
  );
}
