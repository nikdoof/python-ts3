# Last updated: 2011/06/06 (3.0rc1)
# from http://media.teamspeak.com/ts3_literature/TeamSpeak%203%20Server%20Query%20Manual.pdf

# HostMessageMode
HOST_MESSAGE_MODE_LOG = 1 # 1: display message in chatlog
HOST_MESSAGE_MODE_MODAL = 2 # 2: display message in modal dialog
HOST_MESSAGE_MODE_MODALQUIT = 3 # 3: display message in modal dialog and close connection

# CodecType
CODEC_SPEEX_NARROWBAND = 0 # 0: speex narrowband     (mono, 16bit, 8kHz)
CODEC_SPEEX_WIDEBAND = 1 # 1: speex wideband       (mono, 16bit, 16kHz)
CODEC_SPEEX_ULTRAWIDEBAND = 2 # 2: speex ultra-wideband (mono, 16bit, 32kHz)
CODEC_CELT_MONO = 3 # 3: celt mono (mono, 16bit, 48kHz)

# CodecEncryption
CODEC_CRYPT_INDIVIDUAL = 0 # 0: configure per channel
CODEC_CRYPT_DISABLED = 1 # 1: globally disabled
CODEC_CRYPT_ENABLED = 2 # 2: globally enabled

# TextMessageTarget
TEXT_MESSAGE_TARGET_CLIENT = 1 # 1: target is a client
TEXT_MESSAGE_TARGET_CHANNEL = 2 # 2: target is a channel
TEXT_MESSAGE_TARGET_SERVER = 3 # 3: target is a virtual server

# LogLevel
LOGLEVEL_ERROR = 1 # 1: everything that is really bad
LOGLEVEL_WARNING = 2 # 2: everything that might be bad
LOGLEVEL_DEBUG = 3  # 3: output that might help find a problem
LOGLEVEL_INFO = 4 # 4: informational output

# ReasonIdentifier
REASON_KICK_CHANNEL = 4 # kick client from channel
REASON_KICK_SERVER = 5 # kick client from server

# PermissionGroupDatabaseTypes
PERMGROUP_DBTYPE_TEMPLATE = 0 # template group (used for new virtual servers)
PERMGROUP_DBTYPE_REGULAR = 1 # regular group (used for regular clients)
PERMGROUP_DBTYPE_QUERY = 2 # global query group (used for ServerQuery clients)

# PermissionGroupTypes
PERMGROUP_TYPE_SERVERGROUP = 0 # server group permission
PERMGROUP_TYPE_GLOBALCLIENT = 1 # client specific permission
PERMGROUP_TYPE_CHANNEL = 2 # channel specific permission
PERMGROUP_TYPE_CHANNELGROUP = 3 # channel group permission
PERMGROUP_TYPE_CHANNELCLIENT = 4 # channel-client specific permission

# TokenType
TOKEN_SERVER_GROUP = 0 # server group token (id1={groupID} id2=0)
TOKEN_CHANNEL_GROUP = 1 # channel group token (id1={groupID} id2={channelID})

# PermissionAutoUpdateTypes
PERMISSION_AUTOUPDATE_QG = 0 # 0: target will be handled as Query Guest
PERMISSION_AUTOUPDATE_QA = 1 # 1: target will be handled as Query Admin
PERMISSION_AUTOUPDATE_SA = 2 # 2: target will be handled as Server Admin
PERMISSION_AUTOUPDATE_SN = 3 # 3: target will be handled as Server Normal
PERMISSION_AUTOUPDATE_SG = 4 # 4: target will be handled as Server Guest
PERMISSION_AUTOUPDATE_CA = 5 # 5: target will be handled as Channel Admin
PERMISSION_AUTOUPDATE_CO = 6 # 6: target will be handled as Channel Operator
PERMISSION_AUTOUPDATE_CV = 7 # 7: target will be handled as Channel Voice
PERMISSION_AUTOUPDATE_CG = 8 # 8: target will be handled as Channel Guest
