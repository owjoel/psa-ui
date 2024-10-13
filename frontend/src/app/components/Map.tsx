"use client";

import { Box, Divider, Paper, Space, Title, Text, Flex, Badge, Button } from "@mantine/core";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./Map.module.css";
import { useEffect, useState } from "react";
import axios from "axios";

// Define interfaces for the ship and port data
interface Ship {
  name: string;
  LAT: number;
  LON: number;
  SOG: number;
  COG: number;
  Heading: number;
  Length: number;
  Width: number;
  Draft: number;
  distanceToPort: number;
}

interface Port {
  name: string;
  LAT: number;
  LON: number;
}

const nmphToDeg = (nmph: number) => nmph * (1 / 60) / 10; // Adjusted for small interval simulation

// Sample data for ships and ports
const originalShips: Ship[] = [
  // { name: 'Ship A', LAT: 25.76609, LON: -80.14147, SOG: 9.0, COG: 149.9, Heading: 30, Length: 90.0, Width: 13.0, Draft: 4.3, distanceToPort: 0.59 },
  { name: 'Ship A', LAT: 25.68729, LON: -79.93940, SOG: 9.7, COG: -72.2, Heading: 180, Length: 147.0, Width: 23.0, Draft: 8.5, distanceToPort: 12.774887 },
  { name: 'Ship B', LAT: 25.67579, LON: -80.00238, SOG: 12.5, COG: 9.3, Heading: 270, Length: 299.0, Width: 40.0, Draft: 11.7, distanceToPort: 9.89 },
  { name: 'Ship C', LAT: 25.76630, LON: -80.15911, SOG: 0.0, COG: -138.6, Heading: 271.0, Length: 139.0, Width: 22.0, Draft: 7.4, distanceToPort: 0.000598, },
  { name: 'Ship D', LAT: 27.91812, LON: -80.04220, SOG: 16.2, COG: 175.7, Heading: 90, Length: 335.0, Width: 42.0, Draft: 14.6, distanceToPort: 128.899029 },
]; 

const ports: Port[] = [
  { name: 'Port of Miami', LAT: 25.7745, LON: -80.1709 },
];

const portIcon = new L.Icon({
  iconUrl: '/icons/port.png', // Replace with your port icon path
  iconSize: [32, 32],
  iconAnchor: [12, 41],
});

// Function to create a rotating ship icon based on heading
const createShipIcon = (heading: number) => {
  return new L.DivIcon({
    className: "ship-icon", // Use a custom class for styling
    html: `<img src="/icons/ship.png" style="transform: rotate(${heading}deg);" />`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

export default function Map() {
  const [etaResults, setEtaResults] = useState<{ name: string; eta: number }[]>([]);


  const [ships, setShips] = useState(originalShips);
  
  // Update positions based on heading and SOG
  const updateShipPositions = () => {
    setShips((currentShips) =>
      currentShips.map((ship) => {
        const headingRad = (ship.Heading * Math.PI) / 180; // Convert heading to radians
        const distance = nmphToDeg(ship.SOG / 30); // Adjust based on speed and interval duration

        // Calculate new lat and lon based on heading and distance
        const newLat = ship.LAT + distance * Math.cos(headingRad);
        const newLon = ship.LON + distance * Math.sin(headingRad);

        return { ...ship, LAT: newLat, LON: newLon };
      })
    );
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      updateShipPositions();
    }, 600); // 2 minutes in milliseconds

    return () => clearInterval(intervalId);
  }, []);



  const fetchEtaPredictions = async () => {
    try {
      console.log(ships);
      const response = await axios.post('http://127.0.0.1:5000/eta-predict', { ships });
      setEtaResults(response.data);
    } catch (error) {
      console.error('Error fetching ETA predictions:', error);
    }
  };

  useEffect(() => {
    fetchEtaPredictions();
  }, []);

  
  return (
    <Paper withBorder p="md" radius="md" className="flex-1 h-full guide">
      <Flex direction="row" align="center" justify="space-between">
        {/* Map Section */}
        <div className="grow" style={{ flex: 1 }}>
          <Title order={5}>Map</Title>
          <Space h="md" />
          <MapContainer className="h-[35rem] rounded-md" center={[25.7745, -80.1709]} zoom={10} scrollWheelZoom={false}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {/* Render ship markers */}
            {ships.map((ship, index) => (
              <Marker key={`ship-${index}`} position={[ship.LAT, ship.LON]} icon={createShipIcon(ship.Heading)}>
                <Popup>
                  <b>{ship.name}</b><br />
                  Latitude: {ship.LAT}<br />
                  Longitude: {ship.LON}<br />
                  SOG: {ship.SOG}<br />
                  COG: {ship.COG}<br />
                  Heading: {ship.Heading}<br />
                  Length: {ship.Length}<br />
                  Width: {ship.Width}<br />
                  Draft: {ship.Draft}<br />
                </Popup>
              </Marker>
            ))}
            
            {/* Render port markers */}
            {ports.map((port, index) => (
              <Marker key={`port-${index}`} position={[port.LAT, port.LON]} icon={portIcon}>
                <Popup>
                  <b>{port.name}</b><br />
                  Latitude: {port.LAT}<br />
                  Longitude: {port.LON}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Vertical Divider */}
        <Divider orientation="vertical" mx="md" />

        {/* Text Section */}
      <Box style={{ minWidth: '12rem', paddingLeft: '15px' }}>
          {/* Refresh Button */}
          <Button onClick={fetchEtaPredictions} mb="md" fullWidth variant="outline" color="blue" size="xs">
            Refresh ETA
          </Button>
        <Text fz="xs" tt="uppercase" fw={700} color="dimmed" mb="sm">Estimated Time of Arrival</Text>
        
        {/* Map over etaResults to create a styled list */}
        {etaResults.map(({ name, eta }, index) => (
          <Box key={index} mb="sm" p="xs" style={{ borderBottom: '1px solid #f0f0f0' }}>
            <Flex align="center" justify="space-between">
              <Text fz="md" fw={600} style={{ flex: 1 }}>{name}</Text>
              <Badge color="blue" variant="light" style={{ minWidth: '60px', textAlign: 'center' }}>
                {eta.toFixed(2)} mins
              </Badge>
            </Flex>
          </Box>
        ))}
      </Box>

      </Flex>
    </Paper>
  );
}
