###########################################
# Require a commit message as an argument
###########################################

if [ $# -lt 1 ]; then
  echo "Usage: $0 <string>"
  exit 1
fi
arg="$1"

###########################################
# Copy X Controls files (ClyphXPro doesn't allow them to be symlinked from this dir)
###########################################

cp /Users/maxpleaner/nativeKONTROL/ClyphX_Pro/X-Controls.txt X-Controls/X-Controls.txt
cp /Users/maxpleaner/nativeKONTROL/ClyphX_Pro/XTA/X-Controls.txt X-Controls/X-Controls_XTA.txt

###########################################
# Backup to Git
###########################################

git add -A
git commit -m "$arg"
git push origin HEAD
