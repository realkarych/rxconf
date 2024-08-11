<p align="center">
  <a href="https://github.com/realkarych/rxconf">
  <img src="https://github.com/user-attachments/assets/bf4685c0-0d4b-4700-b56f-af751368bca0" alt="RxConf"></a>
</p>

<p align="center">
    <em>RxConf library, easy to use, powerful and flexible for configuration management in Python</em>
</p>

<p align="center">
  <img src="https://realkarych.github.io/rxconf/coverage.svg" alt="Coverage">
  <img src="https://github.com/realkarych/rxconf/actions/workflows/run_tests.yml/badge.svg" alt="Tests status">
</p>

---

**Documentation:** <https://realkarych.github.io/rxconf/>

**Source code:** <https://github.com/realkarych/rxconf/>

---

<h1 align="center">
Currently in develop...
</h1>

- [ ] Implement config loaders:
  - [x] Implement base class which will be inherited by concrete loaders
  - [ ] Implement Environment Variables & `dotenv` loader
  - [ ] Implement `yaml` loader
  - [ ] Implement `toml` loader
  - [ ] Implement `ini` loader
  - [ ] Implement `json` loader

  *Here in-need to minimize deps not from standart library.*

- [ ] Implement reactive config-state observer.
- [ ] Implement async reactive config-state observer.
- [ ] Intruduce testing strategy: validation, race conditions etc.
- [ ] Introduce core API structure and interfaces.
- [ ] Provide examples and usecases for all public interfaces.
