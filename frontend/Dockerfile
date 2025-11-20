# Frontend Dockerfile for Next.js
FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --silent || npm install --silent
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
