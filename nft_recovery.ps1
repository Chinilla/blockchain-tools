param (
    [string]$fingerprint,
    [int]$sleep = 0,
    [string]$nettype = "vanillanet", 
    [string[]]$blockchains = "chinilla",
    [Parameter(Mandatory=$True)][string]$LAUNCHER_HASH,
    [Parameter(Mandatory=$True)][string]$POOL_CONTRACT_ADDRESS)

Install-Module powershell-Yaml -Scope CurrentUser
Push-Location

function Install-blockchaintools {
    if (Test-Path $blockchaintools_check -PathType Leaf) {
        write-log "blockchain-tools already installed"
    }
    else
    {
        
        Set-Location $Env:Userprofile
        git clone https://github.com/Chinilla/blockchain-tools
        write-log "blockchain-tools not present. Installing"  
        Set-Location blockchain-tools
        python -m venv venv
        .\venv\Scripts\activate
        pip install -e . --extra-index-url https://pypi.chia.net/simple/
        deactivate
    }
}

function Get-Rpcport {
    param ([string]$blockchainpath) 
    Write-log "Looking up for a RPC port"
    $configfile = "$blockchainpath\config\config.yaml"

    if (Test-Path $configfile -PathType Leaf) {      
        [string[]]$fileContent = Get-Content $configfile
        $content = ''
        foreach ($line in $fileContent) { $content = $content + "`n" + $line }
        $yaml = ConvertFrom-YAML $content
        $port = $yaml.full_node.rpc_port
        Write-log "Found RPC port nummber: $port"
        return $port
    }
    else
    {
        write-log "Config file missing. Aborting!"
        Terminate
    }
}
function Get-Walletdb {
    param ([string]$blockchainpath) 
    Write-log "Started wallet DB lookup."
    $walletfiles = Get-ChildItem -Path "$blockchainpath\wallet\db\" -Filter "blockchain_wallet*$fingerprint.sqlite"

    if (($walletfiles.count -gt 1))
    {
        write-log "Multiple wallet DB files found. Please choose desired wallet with -fingerprint [fingerprint] paremeter at script startup"
        Foreach ($wallet in $walletfiles)
        {
        $lenght =  $wallet.BaseName.Length
        $cutposition = $wallet.BaseName.LastIndexOf("_") 
        $finferprint = $wallet.BaseName.Substring($cutposition + 1, $lenght - $cutposition - 1)
        $created = $wallet.CreationTime
        $updated = $wallet.LastWriteTime
        
        write-log "Fingerprint: $finferprint, Created: $created, Updated: $updated"
        }
        Terminate
    }  
    elseif ($walletfiles.count -eq 0) 
    {
        write-log "No wallet DB files found!"
        Terminate
    }
    else
    {
        $walletfile = $walletfiles.FullName
        write-log  "Found wallet File $walletfile file"
        Return $walletfile
    }
}

function Get-Blockckchaindb {
    param ([string]$blockchainpath)
    Write-log "Started blockchain DB lookup." 
    $blockchaindbfiles = Get-ChildItem -Path "$blockchainpath\db\" -Filter blockchain_*.sqlite

    if ($blockchaindbfiles.count -gt 1)
    {
        write-log "Unsuported. Multiple Blockchain DB files found. Exiting"
        Foreach ($blockchaindb in $blockchaindbfiles)
        {
        $name =  $blockchaindb.FullName
        $created = $blockchaindb.CreationTime
        $updated = $blockchaindb.LastWriteTime
        
        write-log "Name: $name, Created: $created, Updated: $updated"
        }
        Terminate        
    }  
    elseif ($blockchaindbfiles.count -eq 0) 
    {
        write-log "No Blockchain DB files found!"
        Terminate
    }
    else
    {
        $blockchaindbfile = $blockchaindbfiles.FullName
        write-log  "Found Blockchain File: $blockchaindbfile"
        Return $blockchaindbfile
    }
}

Function Write-log
{
   Param ([string]$logstring)
   $timestamp = Get-TimeStamp
   Write-Host "$timestamp $logstring"
   Add-content $Logfile -value "$timestamp $logstring" -Force
}

function Get-TimeStamp { 
    return "[{0:MM/dd/yy} {0:HH:mm:ss}] " -f (Get-Date)   
}

function Terminate {
    Pop-Location
    Write-host "Program will exit after 10 seconds"
    Start-Sleep -s 10
    Exit
}
function Run-Recovery 
{
    Write-log "Started the blockchain-tools recovery proces for $blockchain"
    Set-Location $Env:Userprofile\blockchain-tools
    .\venv\Scripts\activate
    $blockchaintools_output = blockchain-tools nft-recover -l $LAUNCHER_HASH -p $POOL_CONTRACT_ADDRESS -nh 127.0.0.1 -np $RpcPort -ct $blockchainpath/config/ssl/full_node/private_full_node.crt -ck $blockchainpath/config/ssl/full_node/private_full_node.key  | Out-String
    Write-log $blockchaintools_output
    deactivate
    Pop-Location
    Write-log "Finished the blockchain-tools recovery proces"
   
    
}

$blockchaintools_check = "$Env:Userprofile\blockchain-tools\venv\Scripts\activate" 
$LogFile = "$Env:Userprofile\blockchain-tools\blockchain-tools-output.log"
Install-blockchaintools

Do {
    Foreach ($blockchain in $blockchains) {
        $blockchainpath = "$Env:Userprofile\.$blockchain\$nettype" 
        $Env:BLOCKCHAIN_TOOLS_BC_DB_PATH = Get-Blockckchaindb ($blockchainpath)
        
        $Env:BLOCKCHAIN_TOOLS_WT_DB_PATH = Get-Walletdb ($blockchainpath)
        $RpcPort = Get-Rpcport ($blockchainpath)
        Run-Recovery 
    }
    IF ($sleep-gt 0){
        [int]$SleepHours = $sleep * 3600
        Write-log "Running in a loop. Going to sleep for $sleep minutes"
        Start-Sleep -s $SleepHours
    }
    
} while ($sleep -gt 0)
