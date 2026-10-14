// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      { source: '/k-pop', destination: '/', permanent: true },
      { source: '/k-drama', destination: '/', permanent: true },
      { source: '/k-movie', destination: '/', permanent: true },
      { source: '/k-entertainment', destination: '/', permanent: true },
      { source: '/k-culture', destination: '/culture', permanent: true },
    ];
  },
};

module.exports = nextConfig;
