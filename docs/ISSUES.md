# ISSUES

## kinematic rigid body の位置が GUI レンダラーに反映されない

**症状:** `RigidPrimView.set_world_poses(usd=True)` で Segment_000（kinematic）の位置を毎ステップ更新しても、GUI ウィンドウでは上端が静止したまま。

**ヘッドレスとの矛盾:** `get_world_poses(usd=False)` で読んだ CSV は `err_r=0.0000`（完全追従）を示すが、これは設定したキネマティックターゲット値を読み返しているだけの可能性がある（PhysX が実際には動かしていない）。Fxy≈0.044 N も初期位置 (R,0) からの遠心力によるもので、実際に円運動していなくても発生する。

**仮説:**
1. `set_world_poses` がキネマティックボディに対して PhysX の kinematic target を正しく設定していない
2. `get_world_poses(usd=False)` がキネマティックボディに対して target 値（書き込んだ値）を返す（actual position ではない）
3. Isaac Sim でのキネマティックボディ運動には別の API が必要（`omni.physx` 直接 or `ArticulationView`）

**未解決。** 調査・修正が必要。

---

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
