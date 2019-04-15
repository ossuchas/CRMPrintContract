import os.path
import pyodbc
import logging

class ConnectDB:
    def __init__(self):
        ''' Constructor for this class. '''
        self._connection = pyodbc.connect(
        #    'Driver={SQL Server};Server=192.168.0.37;Database=db_iconcrm_fusion;uid=sa;pwd=P@ssw0rd;')
        'Driver={SQL Server};Server=192.168.0.75;Database=db_iconcrm_fusion;uid=iconuser;pwd=P@ssw0rd;')
        self._cursor = self._connection.cursor()

    def query(self, query):
        try:
            result = self._cursor.execute(query)
        except Exception as e:
            logging.error('error execting query "{}", error: {}'.format(query, e))
            return None
        finally:
            return result

    def update(self, sqlStatement):
        try:
            self._cursor.execute(sqlStatement)
        except Exception as e:
            logging.error('error execting Statement "{}", error: {}'.format(sqlStatement, e))
            return None
        finally:
            self._cursor.commit()

    def exec_sp(self, sqlStatement, params):
        try:
            self._cursor.execute(sqlStatement, params)
        except Exception as e:
            logging.error('error execting Statement "{}", error: {}'.format(sqlStatement, e))
            return None
        finally:
            self._cursor.commit()

    def exec_spRet(self, sqlStatement, params):
        try:
            result = self._cursor.execute(sqlStatement, params)
        except Exception as e:
            print('error execting Statement "{}", error: {}'.format(sqlStatement, e))
            return None
        finally:
            return result

    def __del__(self):
        self._cursor.close()


def getDfltParam():
    """
    index value
    0 = SQL Statement for Main Query
    1 = Excel File Name
    2 = receivers ;
    3 = Subject Mail
    4 = Body Mail
    5 = Footer Mail
    6 = Log Path
    """

    strSQL = """
    SELECT long_desc 
    FROM dbo.CRM_Param
    WHERE param_code = 'CRM_PRNT_CNTR'
    ORDER BY param_seqn
    """

    myConnDB = ConnectDB()
    result_set = myConnDB.query(strSQL)
    returnVal = []

    for row in result_set:
        returnVal.append(row.long_desc)

    return returnVal


def processData(p_pathfile):
    strSQL = """
    SELECT  'A' AS GroupType ,
            b.FolderName ,
            a.ProductID ,
            a.UnitNumber ,
            a.ContractNumber ,
            a.ApprovePrintFlag ,
            c.DisplayName AS ApprovePrintBy ,
            FORMAT(a.ApprovePrintDate, 'dd/MM/yyyy HH:mm') ApprovePrintDate ,
            a.ApprovePrintFile
    FROM    dbo.ICON_EntForms_Agreement a
            LEFT JOIN dbo.Users c ON a.ApprovePrintBy = c.UserID ,
            CRM_PrintContractConf b
    WHERE   a.ApprovePrintBy IS NOT NULL
            AND ISNULL(a.ApprovePrintFlag, 'N') = 'N'
            AND a.ProductID = b.Project
    UNION ALL
    SELECT  'U' AS GroupType ,
            b.FolderName ,
            a.NewProductID ,
            a.UnitNumber ,
            a.ReferentID ,
            a.ApprovePrintFlag ,
            c.DisplayName AS ApprovePrintBy ,
            FORMAT(a.ApprovePrintDate, 'dd/MM/yyyy HH:mm') ApprovePrintDate ,
            a.ApprovePrintFile
    FROM    dbo.ICON_EntForms_UnitHistory a
            LEFT JOIN dbo.Users c ON a.ApprovePrintBy = c.UserID ,
            CRM_PrintContractConf b
    WHERE   a.ApprovePrintBy IS NOT NULL
            AND ISNULL(a.ApprovePrintFlag, 'N') = 'N'
            AND a.NewProductID = b.Project
    """

    myConnDB = ConnectDB()
    result_set = myConnDB.query(strSQL)

    for row in result_set:
        fullPath = p_pathfile + '\\' + row.FolderName + '\\' + row.ProductID
        file_scan = checkFilebyUnit(fullPath, row.UnitNumber)
        if file_scan:
            logging.info("Project {}: This unit No. {}, has a file is {}".format(row.ProductID, row.UnitNumber, file_scan))
            new_file_name = rename_files(fullPath, file_scan)
            updateFlagDB(row.GroupType, row.ProductID, row.UnitNumber, row.ContractNumber, new_file_name)
        else:
            pass
            # logging.info("Project {}: Not Found File Scan in unit No. {}".format(row.ProductID, row.UnitNumber))


def checkFilebyUnit(p_fullPath, p_unit):
    for file in os.listdir(p_fullPath):
        if p_unit in file.upper():
            return file

def rename_files(fullPath, file_scan):
    file_name_old, file_extension = os.path.splitext(file_scan)
    file_name_new = file_name_old + "_Approved" + file_extension
    source = fullPath + '\\' + file_scan
    destination = fullPath + '\\' + file_name_new
    print(source, destination)
    # os.rename(source, destination)
    return destination

def updateFlagDB(grouptype, projectId, unitNo, contractNo, file_name):

    if grouptype == 'A':
        strSQL = """
        UPDATE dbo.ICON_EntForms_Agreement
        SET ApprovePrintFlag = 'Y' ,
        ApprovePrintFile = '{}'
        WHERE ProductID = '{}'
        AND UnitNumber = '{}'
        AND ContractNumber = '{}'
        AND ISNULL(ApprovePrintFlag, 'N') = 'N'
        """.format(file_name, projectId, unitNo, contractNo)
    else:
        strSQL = """
        UPDATE dbo.ICON_EntForms_UnitHistory
        SET ApprovePrintFlag = 'Y' ,
        ApprovePrintFile = '{}'
        WHERE NewProductID = '{}'
        AND UnitNumber = '{}'
        AND ReferentID = '{}'
        AND ISNULL(ApprovePrintFlag, 'N') = 'N'
        """.format(file_name, projectId, unitNo, contractNo)

    myConnDB = ConnectDB()
    myConnDB.update(strSQL)
    logging.info("Effect Data => {} {} {} {} {}".format(grouptype, projectId, unitNo, contractNo, file_name))

def main(dfltVal):
    logging.info("<<<Start>>> Process Data")
    dfltVal[1] = r"\\192.168.2.52\dev2\temp"
    processData(dfltVal[1])
    logging.info("<<<ENd>>> Process Data")


if __name__ == '__main__':
    # Get Default Parameter from DB
    dfltVal = getDfltParam()

    log_path = dfltVal[0]
    logFile = log_path + '\CRMBtchPrintContract.log'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-5s [%(levelname)-8s] >> %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logFile,
                        filemode='a')

    logging.debug('#####################')
    logging.info('Start Process')
    main(dfltVal)
    logging.info('End Process')
    logging.debug('#####################')
