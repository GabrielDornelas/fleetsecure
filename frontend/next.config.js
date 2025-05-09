/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_URL: process.env.API_URL || "http://localhost:8000/api/v1",
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${
          process.env.API_URL || "http://localhost:8000/api/v1"
        }/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
