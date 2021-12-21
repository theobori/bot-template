# 🤖 Discord bot template 

#### How to install dependencies ?

```bash
bash install.sh
```


### Setup bot

1. Install the dependencies 
    - Run the bash script `install.sh` (Can request sudo)
  
2. Create the file `config.ini` in the repository source using the `config_example.ini`
    - Insert a discord token and the api host (`localhost` by default)

3. Import the SQL schema into a db engine, for MySQL:
   - `mysql -u username -p database < data/schema.sql`

4. Execute the file `main.py` with python3 (version <= `3.8`) to start the bot