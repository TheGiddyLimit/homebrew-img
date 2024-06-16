source_json=COMConstruct
git branch "$source_json"
git checkout "$source_json"
git add .
git commit -m "Add $source_json"
git push -u origin "$source_json"
git switch main