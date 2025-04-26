import { useState, useEffect } from "react";
import Head from "next/head";

export default function Home() {
  const [apiStatus, setApiStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );

  useEffect(() => {
    // Verificar status da API ao carregar
    async function checkApi() {
      try {
        const response = await fetch("/api/v1/trucks/");
        if (response.ok) {
          setApiStatus("success");
        } else {
          setApiStatus("error");
        }
      } catch (error) {
        setApiStatus("error");
      }
    }

    checkApi();
  }, []);

  return (
    <>
      <Head>
        <title>FleetSecure | Sistema de Gerenciamento de Frota</title>
        <meta
          name="description"
          content="Gerenciamento de motoristas e caminhões para sua frota"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-100">
        <div className="container mx-auto px-4 py-10">
          <header className="mb-10">
            <h1 className="text-4xl font-bold text-blue-800">FleetSecure</h1>
            <p className="text-gray-600 mt-2">
              Sistema de Gerenciamento de Frota
            </p>
          </header>

          <div className="bg-white shadow-md rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">
              Bem-vindo ao FleetSecure
            </h2>
            <p className="mb-4">
              FleetSecure é uma solução completa para gerenciamento de
              motoristas e caminhões da sua frota.
            </p>

            <div className="mt-6">
              <h3 className="text-lg font-medium mb-2">Status da API:</h3>
              <div className="flex items-center">
                {apiStatus === "loading" && (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-700 mr-2"></div>
                    <span>Verificando conexão...</span>
                  </div>
                )}

                {apiStatus === "success" && (
                  <div className="flex items-center">
                    <div className="bg-green-500 text-white px-3 py-1 rounded-full text-sm mr-2">
                      Online
                    </div>
                    <span>API conectada com sucesso!</span>
                  </div>
                )}

                {apiStatus === "error" && (
                  <div className="flex items-center">
                    <div className="bg-red-500 text-white px-3 py-1 rounded-full text-sm mr-2">
                      Offline
                    </div>
                    <span>
                      Não foi possível conectar à API. Verifique se o backend
                      está rodando.
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">
                Gerenciar Motoristas
              </h2>
              <p className="text-gray-600 mb-4">
                Cadastre e gerencie os motoristas da sua frota, incluindo
                documentação e licenças.
              </p>
              <button
                className="bg-blue-700 hover:bg-blue-800 text-white font-medium py-2 px-4 rounded"
                onClick={() => alert("Funcionalidade em desenvolvimento")}
              >
                Acessar Motoristas
              </button>
            </div>

            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">
                Gerenciar Caminhões
              </h2>
              <p className="text-gray-600 mb-4">
                Registre e monitore todos os caminhões da sua frota, incluindo
                manutenções e atribuições.
              </p>
              <button
                className="bg-blue-700 hover:bg-blue-800 text-white font-medium py-2 px-4 rounded"
                onClick={() => alert("Funcionalidade em desenvolvimento")}
              >
                Acessar Caminhões
              </button>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4">
          <p className="text-center">
            &copy; 2025 FleetSecure. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </>
  );
}
