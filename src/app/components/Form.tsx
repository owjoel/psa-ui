import { Button, Container, Flex, Paper, Space, TextInput, Title } from "@mantine/core";
import classes from "./Form.module.css";
import { IconDownload } from "@tabler/icons-react";

export function Form() {
  return (
    <Paper withBorder p="md" radius="md" className="flex-1">
      <Title order={5}>Schedule Frieghter </Title>
      <Flex
        mih={50}
        gap="xs"
        justify="flex-start"
        align="flex-start"
        direction="column"
        wrap="wrap"
      >
        <TextInput
          label="Shipping address"
          placeholder="15329 Huston 21st"
          classNames={classes}
        />
        <TextInput
          label="Shipping address"
          placeholder="15329 Huston 21st"
          classNames={classes}
        />
        <TextInput
          label="Shipping address"
          placeholder="15329 Huston 21st"
          classNames={classes}
        />
        <TextInput
          label="Shipping address"
          placeholder="15329 Huston 21st"
          classNames={classes}
        />
      </Flex>
      <Space h="lg" />
      <Button rightSection={<IconDownload size={14} />}>Download</Button>
    </Paper>
  );
}
