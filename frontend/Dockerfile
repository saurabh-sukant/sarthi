# Build stage
FROM node:18-alpine AS builder
 
WORKDIR /app
 
ARG VITE_API_BASE_URL=http://sarthi-api:8000
 
COPY package.json ./
 
RUN npm install
 
COPY src ./src
COPY index.html vite.config.js ./
 
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL npm run build
 
# Production stage
FROM node:18-alpine
 
WORKDIR /app
 
RUN npm install -g serve
 
COPY --from=builder /app/dist ./dist
 
EXPOSE 5173
 
CMD ["serve", "-s", "dist", "-p", "5173"]