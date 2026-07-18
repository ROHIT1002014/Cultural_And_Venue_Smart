# syntax=docker/dockerfile:1.4
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

# Stage 1: Development Server
FROM base AS development
EXPOSE 5173
CMD ["npm", "run", "dev"]

# Stage 2: Build Frontend Assets
FROM base AS build
RUN npm run build

# Stage 3: Production Nginx Server
FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
# Include default nginx SPA routing
RUN echo 'server { listen 80; location / { root /usr/share/nginx/html; index index.html; try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
