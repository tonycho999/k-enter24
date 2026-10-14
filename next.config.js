/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return ['k-pop', 'k-drama', 'k-movie', 'k-entertainment', 'k-culture'].map((cat) => ({
      source: `/${cat}`,
      destination: '/',
      permanent: true,
    }));
  },
};

module.exports = nextConfig;
