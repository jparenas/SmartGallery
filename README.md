Start development server:

```
docker-compose -f docker-compose.dev.yml down && docker-compose -f docker-compose.dev.yml build && docker-compose -f docker-compose.dev.yml up
```

Build and start production server:

```
docker-compose down && docker-compose build && docker-compose up
```