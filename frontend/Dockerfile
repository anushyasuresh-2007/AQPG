# Stage 1: Build the React client app
FROM node:20-alpine AS build

WORKDIR /app

# Copy package lock and config
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy all sources and build static bundle
COPY . .
RUN npm run build

# Stage 2: Serve compiled HTML/JS files via Nginx
FROM nginx:stable-alpine

# Copy built static files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for SPA routing and proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
