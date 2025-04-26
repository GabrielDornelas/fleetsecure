import React, { ReactNode } from "react";
import Head from "next/head";

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export default function Layout({
  children,
  title = "FleetSecure",
}: LayoutProps) {
  return (
    <>
      <Head>
        <title>{title} | Sistema de Gerenciamento de Frota</title>
        <meta
          name="description"
          content="Gerenciamento de motoristas e caminhões para sua frota"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen flex flex-col">
        <header className="bg-white shadow-md">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-800">FleetSecure</h1>
            </div>
            <nav>
              <ul className="flex space-x-6">
                <li>
                  <a className="hover:text-blue-600" href="/">
                    Início
                  </a>
                </li>
                <li>
                  <a className="hover:text-blue-600" href="/users">
                    Motoristas
                  </a>
                </li>
                <li>
                  <a className="hover:text-blue-600" href="/trucks">
                    Caminhões
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </header>

        <main className="flex-grow">
          <div className="container mx-auto px-4 py-8">{children}</div>
        </main>

        <footer className="bg-gray-800 text-white py-6">
          <div className="container mx-auto px-4">
            <p className="text-center">
              &copy; 2025 FleetSecure. Todos os direitos reservados.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
