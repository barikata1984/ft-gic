# ISSUES

## `/isaac-sim/kit/` キャッシュディレクトリ書き込み不可

**症状:** GUI/headless 起動時に以下のエラーが大量出力される。
```
[Error] [omni.datastore] Failed to create local file data store at '/isaac-sim/kit/cache/DerivedDataCache'
[Error] [gpu.foundation.plugin] Failed to initialize rtx::shaderdb::ContextManager
```

**原因:** Kit `--portable` モードが `/isaac-sim/kit/cache/`, `/isaac-sim/kit/data/`, `/isaac-sim/kit/logs/` に書き込もうとするが、これらは `isaac-sim` ユーザー（uid=1234）所有でコンテナ内の実行ユーザー（uid=1000）には書き込み権限がない。
DerivedDataCache（UJITSO）が機能しないとアセットの処理・ダウンロードが正常に行えない。

**対処済み:** `docker/Dockerfile` に以下を追加済み。コンテナリビルドで解消する。
```dockerfile
RUN mkdir -p /isaac-sim/kit/cache /isaac-sim/kit/data /isaac-sim/kit/logs \
    && chown ${HOST_UID}:${HOST_GID} \
         /isaac-sim/kit/cache \
         /isaac-sim/kit/data \
         /isaac-sim/kit/logs
```

**残作業:** `docker compose build && docker compose up -d` でリビルド・再起動。
