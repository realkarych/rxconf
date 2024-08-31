# Why Use RxConf?

- **Realtime Observers:** You can use triggers to specify actions that
should occur when configuration attributes change.
This helps in organizing hot-reload applications.
- **Scalability:** RxConf is designed using OOP patterns and provides
interfaces to implement your own ConfigTypes, triggers, and more.
- **Support for Popular Config Types:** Currently, RxConf supports `yaml`, `toml`, `json`, `ini`, `dotenv`
files, and environment variables.
And all of these manages through a single interface.
- **Asyncio Support:** RxConf is compatible with `asyncio`, allowing you to use it seamlessly in asynchronous applications.
- **Performance:** RxConf uses optimizations and heuristics to control and update config states.
Works so fast that you won't even notice it's working. We promise.
