"use client";

import { Paper, Space, Title } from "@mantine/core";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./Map.module.css"

export default function Map() {
  
  return (
    <Paper withBorder p="md" radius="md" className="flex-1 h-full guide">
      <Title order={5}>Map</Title>
      <Space h="md" />
      <MapContainer className="h-[25rem] rounded-md" center={[0,0]} zoom={1} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[51.505, -0.09]}>
          <Popup>
            A pretty CSS3 popup. <br /> Easily customizable.
          </Popup>
        </Marker>
      </MapContainer>
    </Paper>
  );
}
