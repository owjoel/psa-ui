"use client";

import { Form } from "@/app/components/Form";
import PortUsage from "@/app/components/PortUsage";
import { StatsGrid } from "@/app/components/StatsGrid";
// import { Flex, Space, Title } from "@mantine/core";
import Image from 'next/image';
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
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
import axios from "axios";

export default function Dashboard() {
  // Dynamically load map component
  const Map = dynamic(() => import("@/app/components/Map"), {
    loading: () => <p>Loading Map</p>,
    ssr: false,
  });

  const [selectedShip, setSelectedShip] = useState<string | null>(null);
  const [assignedBerth, setAssignedBerth] = useState<string>('N/A');
  const [waitingTime, setWaitingTime] = useState<number | null>(null);

  // Function to handle the ship click
  const handleShipClick = (shipName: string) => {
    predictLowestWtBerth()
    setSelectedShip(shipName); // Update the state with the selected ship name
    console.log(shipName)
  };

  const predictLowestWtBerth = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/predict_lowest_wt_berth');
      const { berth, waiting_time } = response.data;
      setAssignedBerth(berth);
      setWaitingTime(waiting_time);
    } catch (error) {
      console.error('Error fetching berth prediction:', error);
    }
  };

  return (
    <div className="p-6">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
        <Image src="/icons/psa.png" alt="Logo" width={90} height={45} />
        <Title order={3} style={{ marginLeft: '1rem' }}>Live AIS Dashboard</Title>
      </div>
      {/* <Space h="lg" /> */}
      {/* <StatsGrid /> */}
      {/* <Space h="lg" /> */}
      <Map onShipClick={handleShipClick} />
      {/* <Space h="lg" /> */}
      <Flex
        mih={45}
        gap="md"
        justify="center"
        align="center"
        direction="row"
        wrap="wrap"
      // h="24rem"
      >

        <Paper withBorder p="md" radius="md" h="40%" className="flex-1 ">
          <Flex>
            <div className="grow">
              <Title order={6}>Recommended Berth for {selectedShip}</Title>
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
              <Button rightSection={<IconCrane size={14} />} onClick={predictLowestWtBerth}>Recompute Best Berth</Button>
            </div>
            <Divider orientation="vertical" />
            <Box w="20rem" pl={10}>
              <Text fz="xs" tt="uppercase" fw={700} c="dimmed">Assigned</Text>
              <Text fz="xl" fw={700}>{assignedBerth}</Text> {/* Display the assigned berth */}
            </Box>
            <Divider orientation="vertical" />
            <Box w="30rem" pl={10}>
              <Text fz="xs" tt="uppercase" fw={700} c="dimmed">Estimated Waiting Time Before Serviced</Text>
              <Text fz="xl" fw={700}>{waitingTime !== null ? `${waitingTime} hrs` : 'N/A'}</Text> {/* Display the waiting time */}
            </Box>
          </Flex>
        </Paper>
        {/* <Form /> */}
        {/* <PortUsage/> */}
      </Flex>


    </div>
  );
}
