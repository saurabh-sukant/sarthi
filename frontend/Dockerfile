# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY src ./src
COPY index.html vite.config.js ./

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist

EXPOSE 5173

ENV VITE_API_BASE_URL=http://sarthi-api:8000

CMD ["serve", "-s", "dist", "-l", "5173"]
