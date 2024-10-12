import { Navbar } from "@/app/components/Navbar";
import { Flex } from "@mantine/core";
import { ReactNode } from "react";

export default function AdminLayout({ children }: { children: ReactNode }) {
    return (
      <main className="h-full">
        <Flex>
          <Navbar />
          <div style={{ width: '100%', overflowX: 'auto' }}>
            {children}
          </div>
        </Flex>
  
      </main>
    );
  }