import { test, expect } from "@playwright/test";

test.describe("Página Inicial", () => {
  test("deve exibir os elementos corretos", async ({ page }) => {
    // Navegar para a página inicial
    await page.goto("/");

    // Verificar título da página
    await expect(page).toHaveTitle(/FleetSecure/);

    // Verificar se o cabeçalho está presente
    const heading = page.locator('h1:has-text("FleetSecure")');
    await expect(heading).toBeVisible();

    // Verificar se há dois cards (motoristas e caminhões)
    const cards = page.locator(".bg-white.shadow-md.rounded-lg.p-6");
    await expect(cards).toHaveCount(3); // Um card principal e dois de funcionalidades

    // Verificar se os botões estão presentes
    const buttons = page.locator('button:has-text("Acessar")');
    await expect(buttons).toHaveCount(2);
  });

  test("deve mostrar status da API", async ({ page }) => {
    // Navegar para a página inicial
    await page.goto("/");

    // Verificar se o indicador de status da API está presente
    const apiStatus = page.locator("text=Status da API");
    await expect(apiStatus).toBeVisible();

    // Verificar se o status muda de "Verificando conexão..." para um estado final
    // Aguarda até 5 segundos para que o status mude
    await page
      .waitForSelector("text=Online", { state: "visible", timeout: 5000 })
      .catch(() => {
        // Se "Online" não aparecer, "Offline" deve estar visível
        return page.waitForSelector("text=Offline", { state: "visible" });
      });
  });
});
