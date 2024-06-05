# WIMU_Final_project
```sh
# build environment
docker compose up

# if need to rebuild enviroment
docker compose up --build

# backend service will auto start
# open another terminal to manual activate frontend webpage
docker compose exec web bash
npm install # first run
npm run dev
```