FROM node:22-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web .
RUN npm run build
CMD ["npm", "run", "start"]
