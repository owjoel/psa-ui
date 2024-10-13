import { Form } from "@/app/components/Form";
import PortUsage from "@/app/components/PortUsage";
import { StatsGrid } from "@/app/components/StatsGrid";
import { Flex, Space, Title } from "@mantine/core";
import Image from 'next/image';
import dynamic from "next/dynamic";

export default function Dashboard() {
  // Dynamically load map component
  const Map = dynamic(() => import("@/app/components/Map"), {
    loading: () => <p>Loading Map</p>,
    ssr: false,
  });
  return (
    <div className="p-6">
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
      <Image src="/icons/psa.png" alt="Logo" width={100} height={50} />
      <Title order={3} style={{ marginLeft: '1rem' }}>Live AIS Dashboard</Title>
    </div>
      {/* <Space h="lg" /> */}
      {/* <StatsGrid /> */}
      <Space h="lg" />
      <Map />
      {/* <Space h="lg" /> */}
      <Flex
        mih={50}
        gap="md"
        justify="center"
        align="center"
        direction="row"
        wrap="wrap"
        // h="24rem"
      >
        <Form />
        {/* <PortUsage/> */}
      </Flex>


    </div>
  );
}
