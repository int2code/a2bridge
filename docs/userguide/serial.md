# Virtual COM port communication

## Human readable console

One of the USB endpoints is virtual COM port which can be controlled as
any other COM port e.g. with Putty serial. Since it is USB virtal COM
port **the baudrate can be set to any value.** There are few commands
available on COM console depending on the device A2B role.

![image_alt](assets/image6.tmp)


### Console commands in Master mode.

**Following console commands are available in Master mode:**

#### reset 
Resets the device

#### info 
Prints the information about the device

#### status 
Prints the status of the device. Contains the information about the number of slaves discovered and current A2B status.

#### resetjson 
resets the CONFIG.TXT Json file to default one.

#### discover
Performs A2B discovery and updates the number of
discovered A2B slaves.

#### switchproto
Switches COM port to protobuf mode

#### loglevel
Changes the log level. Must to be set to one of these values - \["off", "info", "warning", "error"\]

#### regs
Prints the A2B transceiver registers and its values. If the number of subnode is provided (in master mode) then prints the register values from the subnode transceiver.
Usage: regs / regs 0



### Console commands in Slave mode.

**Following console commands are available in Slave mode:**

#### reset 
Resets the device

#### info
Prints the information about the device

#### status
Prints the status of the device.

#### resetjson
Resets the CONFIG.TXT Json file to default one.

#### switchproto
Switches COM port to protobuf mode

## Protobuf mode

Device can be set to use the protobuf mode via UART instead of text mode.

### Reset
Resets the device

#### **Message properties**
None
#### **Response**
Positive or negative response.


### Status
Sends the response with current status of the device depending on the A2B Role

#### **Message properties**
None

#### **Response**

Common for slave and Master mode:

**usb_audio_downstream_state** - Enumerate with current downstream USB state. Contains one of the following values:



```
    USB_AUDIO_STREAM_STATE_UNSPECIFIED = 0;
    USB_AUDIO_STREAM_STATE_IDLE = 1;
    USB_AUDIO_STREAM_STATE_STREAMING = 2;
```
 

**usb_audio_upstream_state** - Enumerate with current upstream audio USB state. 


```
  USB_AUDIO_STREAM_STATE_UNSPECIFIED = 0;
  USB_AUDIO_STREAM_STATE_IDLE = 1;
  USB_AUDIO_STREAM_STATE_STREAMING = 2;
```

**device_state** - enumerate with current device status

```
  DEVICE_STATE_UNSPECIFIED = 0;
  DEVICE_STATE_BOOT = 1;
  DEVICE_STATE_NORMAL = 2;
  DEVICE_STATE_IMPAIRED = 3;
  DEVICE_STATE_ERROR = 4;
```
**config_json_state** - enumerate with current json config status

```
  CONFIG_JSON_STATE_UNSPECIFIED = 0;
  CONFIG_JSON_STATE_VALID = 1;
  CONFIG_JSON_STATE_INVALID = 2;
```

Master:


**A2bFault** - (optional) Structure containing the information about existing fault in A2B transceiver. This message has following properties:

**fault** - enumerate with current fault type on A2B transceiver




```
  LIBAD243X_FAULTTYPE_NONE = 0,
  LIBAD243X_FAULTTYPE_BECOVF = 1,
  LIBAD243X_FAULTTYPE_SRF_MISS = 2,
  LIBAD243X_FAULTTYPE_PWR_SHRT2GND = 3,
  LIBAD243X_FAULTTYPE_PWR_SHRT2VBAT = 4,
  LIBAD243X_FAULTTYPE_PWR_SHRT2GTHR = 5,
  LIBAD243X_FAULTTYPE_PWR_OPEN = 6,
  LIBAD243X_FAULTTYPE_PWR_REVERSE = 7,
  LIBAD243X_FAULTTYPE_PWR_OTHER = 8,
  LIBAD243X_FAULTTYPE_PWR_NL_SHRT2GND = 9,
  LIBAD243X_FAULTTYPE_PWR_NL_SHRT2VBAT = 10,
  LIBAD243X_FAULTTYPE_TIMEOUT = 11,
  LIBAD243X_FAULTTYPE_MSTR_RESET = 12,
  LIBAD243X_FAULTTYPE_OTHER = 13,
```

**location** - enumerate containing the location of fault source


```
LIBAD243X_FAULTSOURCE_MASTER = 0,
LIBAD243X_FAULTSOURCE_SLAVE = 1,
```
**slave_with_fault** - (optional) If the fault source is slave contains the slave index.

**a2b_slaves_discovered** - number of slaves discovered

Slave:

a2b_state - A2B slave state



  SLAVE_A2B_STATE_UNSPECIFIED = 0;
  SLAVE_A2B_STATE_INIT = 1;
  SLAVE_A2B_STATE_WAIT_DISCOVER = 2;
  SLAVE_A2B_STATE_READY = 3;
  SLAVE_A2B_STATE_NOT_READY = 4;
Info - Request information about the device
**Message properties:**
None
**Response:**

**hardware_revision** - Hardware revision number

**software_revision** - String with software revision

**serial_number** - String with serial number

 

### A2BDiscoveryRequest 
Request A2B bus slave re-discovery

#### **Message properties**

None

#### **Response**
Positive or negative

 

### I2cOverDistance 
Send I2C command over A2B bus to one of the slaves or its peripheral.

#### **Message properties**

**I2cOverDistanceAccessType** - Access type enumerate:


```
  I2C_OVER_DISTANCE_UNSPECIFIED = 0;
  I2C_OVER_DISTANCE_WRITE = 1;
  I2C_OVER_DISTANCE_READ = 2;
```
**peripheral_i2c_addr**  - (optional) if this property is set I2C message will be forwarded to slaves perihperal.

**node** - the index of the node to which the message will be sent or read.

**Data** - Data to send or read 

**reg** - Register to read/write

**value** - Value to write in case of I2C_OVER_DISTANCE_WRITE access type

#### **Response:**

**access_type** - Access type enumerate:



  I2C_OVER_DISTANCE_UNSPECIFIED = 0;
  I2C_OVER_DISTANCE_WRITE = 1;
  I2C_OVER_DISTANCE_READ = 2;
**value** - the value read from the register

 

### A2BMailboxTransfer 
Request to read/write A2B mailbox.

#### **Message properties**

**mailbox_id** - Mailbox identifier

**access_type** - Access type enumerate:

```
  A2B_MAILBOX_ACCESS_TYPE_UNSPECIFIED = 0;
  A2B_MAILBOX_ACCESS_TYPE_WRITE = 1;
  A2B_MAILBOX_ACCESS_TYPE_READ = 2;
```
**node** - node identifier to which the message will be sent/read.

**bytes** - length of the mailbox message (has to be lower than 4 bytes)

#### **Response**

**mailbox_id** - Mailbox identifier

**access_type** - Access type enumerate:


```
  A2B_MAILBOX_ACCESS_TYPE_UNSPECIFIED = 0;
  A2B_MAILBOX_ACCESS_TYPE_WRITE = 1;
  A2B_MAILBOX_ACCESS_TYPE_READ = 2;
```
**access_status** - Status of the read/write to mailbox.



```
  A2B_MAILBOX_STATUS_UNSPECIFIED = 0;
  A2B_MAILBOX_STATUS_OK = 1;
  A2B_MAILBOX_STATUS_GENERAL_FAIL = 2;
  A2B_MAILBOX_STATUS_NOT_EMPTY = 3;
  A2B_MAILBOX_STATUS_NOT_FULL = 4;
```
**data** - data read from the mailbox 