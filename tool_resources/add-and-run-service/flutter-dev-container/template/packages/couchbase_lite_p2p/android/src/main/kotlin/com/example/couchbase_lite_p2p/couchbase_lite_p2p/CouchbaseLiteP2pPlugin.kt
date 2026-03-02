package com.example.couchbase_lite_p2p.couchbase_lite_p2p

import android.content.Context
import android.os.Handler
import android.os.Looper
import com.couchbase.lite.*
import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.MethodChannel.MethodCallHandler
import io.flutter.plugin.common.MethodChannel.Result
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.URI

/** CouchbaseLiteP2pPlugin */
class CouchbaseLiteP2pPlugin : FlutterPlugin, MethodCallHandler {
    private lateinit var channel: MethodChannel
    private lateinit var context: Context
    
    private lateinit var database: Database
    private lateinit var multipeerSyncManager: MultipeerSyncManager
    private var replicator: Replicator? = null
    private val scope = CoroutineScope(Dispatchers.Main)
    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onAttachedToEngine(flutterPluginBinding: FlutterPlugin.FlutterPluginBinding) {
        context = flutterPluginBinding.applicationContext
        channel = MethodChannel(flutterPluginBinding.binaryMessenger, "couchbase_lite_p2p")
        channel.setMethodCallHandler(this)
        
        initializeCouchbase()
    }

    private fun initializeCouchbase() {
        // Initialize Couchbase Lite
        CouchbaseLite.init(context)
        
        // Open Database
        val config = DatabaseConfiguration()
        database = Database(AppConfig.DATABASE_NAME, config)
        
        // Initialize Sync Manager
        multipeerSyncManager = MultipeerSyncManager(context, database)
        
        // Listen for DB changes
        setupDatabaseListeners()
        
        // Listen for P2P status changes
        setupP2PListeners()
    }

    private fun startSyncGatewayReplication(urlString: String) {
        try {
            val url = URI(urlString)
            val target = URLEndpoint(url)
            // Try using named arguments to avoid ambiguity
            val config = ReplicatorConfiguration(target)
            // Use fully qualified enum if needed, or rely on default (PUSH_AND_PULL)
            // config.replicatorType = ReplicatorType.PUSH_AND_PULL 
            config.isContinuous = true
            // addCollection might require a config object in some versions
            config.addCollection(database.defaultCollection, null)
            
            replicator = Replicator(config)
            
            replicator?.addChangeListener { change ->
                val status = change.status
                val statusStr = when (status.activityLevel) {
                    ReplicatorActivityLevel.STOPPED -> "Stopped"
                    ReplicatorActivityLevel.OFFLINE -> "Offline"
                    ReplicatorActivityLevel.CONNECTING -> "Connecting"
                    ReplicatorActivityLevel.IDLE -> "Idle"
                    ReplicatorActivityLevel.BUSY -> "Busy"
                }
                
                val errorStr = status.error?.message
                
                val statusMap = mapOf(
                    "status" to statusStr,
                    "error" to errorStr
                )
                
                mainHandler.post {
                    channel.invokeMethod("onSyncGatewayStatusChanged", statusMap)
                }
            }
            
            replicator?.start()
        } catch (e: Exception) {
            println("SyncGateway: Failed to start replication: ${e.message}")
            mainHandler.post {
                channel.invokeMethod("onSyncGatewayStatusChanged", mapOf(
                    "status" to "Error",
                    "error" to e.message
                ))
            }
        }
    }

    private fun setupDatabaseListeners() {
        val collection = database.defaultCollection
        collection.addDocumentChangeListener("counter") { change ->
            val doc = collection.getDocument(change.documentID)
            if (doc != null) {
                val count = doc.getInt("count")
                mainHandler.post {
                    channel.invokeMethod("onCountChanged", count)
                }
            }
        }
    }

    private fun setupP2PListeners() {
        scope.launch {
            multipeerSyncManager.syncState.collect { state ->
                val statusMap = mutableMapOf(
                    "isRunning" to state.isRunning,
                    "myPeerID" to (state.myPeerID ?: ""),
                    "connectedPeers" to state.connectedPeers.size,
                    "status" to state.syncStatus
                )
                if (state.error != null) {
                    statusMap["error"] = state.error
                }
                mainHandler.post {
                    channel.invokeMethod("onP2PStatusChanged", statusMap)
                }
            }
        }
    }

    override fun onMethodCall(call: MethodCall, result: Result) {
        when (call.method) {
            "increment" -> {
                scope.launch {
                    try {
                        val newCount = incrementCounter()
                        result.success(newCount)
                    } catch (e: Exception) {
                        result.error("DB_ERROR", e.message, null)
                    }
                }
            }
            "getCount" -> {
                scope.launch {
                    try {
                        val count = getCounter()
                        result.success(count)
                    } catch (e: Exception) {
                        result.error("DB_ERROR", e.message, null)
                    }
                }
            }
            "startP2P" -> {
                multipeerSyncManager.start()
                result.success(true)
            }
            "getP2PStatus" -> {
                val state = multipeerSyncManager.syncState.value
                val statusMap = mutableMapOf(
                    "isRunning" to state.isRunning,
                    "myPeerID" to (state.myPeerID ?: ""),
                    "connectedPeers" to state.connectedPeers.size,
                    "status" to state.syncStatus
                )
                if (state.error != null) {
                    statusMap["error"] = state.error
                }
                result.success(statusMap)
            }
            "startSyncGatewayReplication" -> {
                val url = call.argument<String>("url")
                if (url != null) {
                    startSyncGatewayReplication(url)
                    result.success(true)
                } else {
                    result.error("INVALID_ARGS", "URL is required", null)
                }
            }
            else -> {
                result.notImplemented()
            }
        }
    }
    
    private suspend fun incrementCounter(): Int = withContext(Dispatchers.IO) {
        val collection = database.defaultCollection
        val doc = collection.getDocument("counter")?.toMutable() ?: MutableDocument("counter")
        val count = doc.getInt("count")
        val newCount = count + 1
        doc.setInt("count", newCount)
        collection.save(doc)
        return@withContext newCount
    }
    
    private suspend fun getCounter(): Int = withContext(Dispatchers.IO) {
        val collection = database.defaultCollection
        val doc = collection.getDocument("counter")
        return@withContext doc?.getInt("count") ?: 0
    }

    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel.setMethodCallHandler(null)
        multipeerSyncManager.stop()
        replicator?.stop()
        try {
            database.close()
        } catch (e: Exception) {
            // Ignore
        }
    }
}
