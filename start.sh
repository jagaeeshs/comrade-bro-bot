if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/LazyDeveloperr/LazyPrincess-AT.git /LazyPrincess-AT
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /LazyPrincess-AT
fi
cd /LazyPrincess-AT
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
