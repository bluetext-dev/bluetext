package com.example.couchbase_lite_p2p.couchbase_lite_p2p

object AppConfig {
    // Database Configuration
    const val DATABASE_NAME = "counter_db"
    const val COLLECTION_NAME = "_default" // Using default collection for simplicity
    const val SCOPE_NAME = "_default"

    // Sync Gateway Configuration
    // Use 10.0.2.2 for Android Emulator to reach host localhost
    private const val DEFAULT_SYNC_URL = "ws://10.0.2.2:4984/main"
    
    // TODO: Allow configuration from Dart or App
    val syncGatewayURL: String = DEFAULT_SYNC_URL

    val username: String = "user" // Default user
    val password: String = "password" // Default password

    // P2P Configuration
    const val P2P_PEER_GROUP_ID = "com.example.counterapp" // Keep same group ID to sync with native app if needed
    const val P2P_IDENTITY_LABEL = "com.example.counterapp.p2p.identity"
    const val P2P_AUTO_START = true
}
