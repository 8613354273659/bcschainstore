from boa.blockchain.vm.Neo.Runtime import Log, Notify, GetTrigger, CheckWitness
from boa.blockchain.vm.Neo.TriggerType import Application, Verification
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete

from boa.code.builtins import concat, list, range, take, substr

BCSCHAIN = b'\x0b\xf5\xe0J\xffj\x97\x03\\\xdeH\x98i\x86\xf4\xe3\xfa`\x9fy'
VERSION = 1

def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        is_owner = CheckWitness(BCSCHAIN)

        if is_owner:
            return True

        return False

    elif trigger == Application():
        # Check the version for compatability
        if operation == 'ownArea':
            if (len(args) == 3):
                addr = args[0]
                lat = args[1]
                lon = args[2]

                Log('Owning_Area')
                res = own_area(addr,lat,lon)
                return res
            else:
                Log('INVALID_ARGUMENTS')
                return False

        elif operation == 'createProduct':
            if (len(args) == 3):
                addr = args[0]
                uuid = args[1]

                Log('Creating_Product')
                res = create_product(addr,uuid)
                return res
            else:
                Log('INVALID_ARGUMENTS')
                return False
                
        elif operation == 'activateProduct':
            if (len(args) == 2):
                addr = args[0]
                uuid = args[1]

                Log('Activating_Product')
                res = activate_product(addr ,uuid)
                return res
            else:
                Log('INVALID_ARGUMENTS')
                return False
        
        elif operation == 'setPrice':
            if (len(args) == 3):
                addr = args[0]
                uuid = args[1]
                price = args[2]

                Log('Setting_Price')
                res = set_price(addr,uuid,price)
                return res
            else:
                Log('INVALID_ARGUMENTS')
                return False


        elif operation == 'buyProduct':
            if (len(args) == 2):
                addr = args[0]
                uuid = args[1]

                Log('Buying_Product')
                res = buy_product(addr,uuid)
                return res

            else:
                Log('INVALID_ARGUMENTS')
                return False

        elif operation == 'deactivateProduct':
            if (len(args) == 2):
                addr = args[0]
                uuid = args[1]

                Log('Deactivating_Product')
                res = deactivate_product(addr,uuid)
                return res

            else:
                Log('INVALID_ARGUMENTS')
            return False

        Log('INVALID_FUNCTION')
        return False

    Log('FORBIDDEN')
    return False

def own_area(owner_address , lat, lon) :
    if not CheckWitness(owner_address):
        Log('ALREADY')
        return False
    context = GetContext()
    address = Get(context, owner_address)
    obj = [lat,lon]
    location = _data_packing(obj)
    
    if (address == 0):
        Put(context, owner_address, location)
        Log('owned_success')
        return True

    return False

def create_product(owner_address , uuid) :
    if not CheckWitness(owner_address):
        Log('FORBIDDEN')
        return False
    
    if not (CheckUUID(uuid)):
        return False

    if is_owned_area(owner_address):
        context = GetContext()
        price = 0
        status = 'inactive'
        obj = [owner_address,price,status]
        product_data = _data_packing(obj)
        Put(context, uuid, product_data)
        Log('Product_Created')
        return True
    
    return False

def set_price(owner_address , uuid, price) :
    if not CheckWitness(owner_address):
        Log('FORBIDDEN')
        return False

    if not (CheckUUID(uuid)):
        return False
    
    if is_owned_product(uuid,owner_address) :
        context = GetContext()
        status = 'active'
        obj = [owner_address,price,status]
        product_data = _data_packing(obj)
        Put(context, uuid, product_data)
        Log('SUCCESS')
        
        return True
    
    return False

def activate_product(owner_address , uuid) :
    if _set_product_status(owner_address,uuid,'active') :
        Log('ACTIVE_SUCCESS')
        return True
    
    return False

def deactivate_product(owner_address ,uuid):
    if _set_product_status(owner_address,uuid,'inactive') :
        Log('DEACTIVE_SUCCESS')
        return True

    return False

def buy_product(buyer_address , uuid):
    if not CheckWitness(buyer_address):
        Log('FORBIDDEN')
        return False
    
    return False

def _set_product_status(owner_address,uuid,status):
    if not CheckWitness(owner_address):
        Log('FORBIDDEN')
        return False
    
    if not (CheckUUID(uuid)):
        return False
    
    if is_owned_product(uuid,owner_address) :
        context = GetContext()
        product_data_get = Get(context, uuid)
        price = _get_price(product_data_get)
        obj = [owner_address,price,status]
        product_data = _data_packing(obj)
        Put(context, uuid, product_data)
        
        return True

    return False

def is_owned_area(owner_address):
    
    return True

def is_owned_product(uuid,owner_address):
    
    return True

def _get_price(product_data) :
    product_data_unpack = _data_unpacking(product_data)
    price = product_data_unpack[1]

    return price

def CheckUUID(uuid):
    Log("CHECK_UUID_LEN")
    if (len(uuid) != 36):
        Log('UUID_INVALID_LEN')
        return False

    Log("CHECK_UUID_DASH")
    dashes = [8, 13, 18, 23]
    for dash in dashes:
        if not (uuid[dash:dash+1] == '-'):
            Log('UUID_INVALID_DASH')
            return False

    Log("CHECK_UUID_VERSION")
    if not (uuid[14:15] == '4'):
        Log('UUID_INVALID_VERSION')
        return False

    Log('UUID_VALID')
    return True


# helper function for data handling
def _data_unpacking(data_str):
    output = list()
    str_tmp=''
    for c in data_str :
        if (c == ';'):
            output.append(str_tmp)
            str_tmp = ''
        else :
            str_tmp = str_tmp+c
            
    return output

def _data_packing(items):
    output_str = ''
    for item in items:
        output_str = concat(output_str,item)
        output_str = concat(output_str,';')
    
    return output_str

