cbl rent,data(31),lib                                                           
                                                                                
       Identification Division.   *> non mainframe standard comment!                                             
       Program-id. horror.                                                      
       Author . datim.                                                          
       REMARKS. IL EST VRAIMENT HORRIBLE!                                       
       DATE-WRITTEN. AOUT 2010                                                  
      *************************************************************             
            MODULE A RIEN FAIRE:                                                
                      SYNTAXIQUEMENT CORRECT                                    
                      MAIS  NON COMPILABLE !                                    
      *************************************************************             
       Environment Division .                                                   
       Configuration Section .                                                  
      *Source-Computer.                                                         
       Source-Computer . IBM-370 With Debugging Mode.                           
      *Source-Computer . IBM-370.                                               
       Object-computer.                                                         
           IBM-370.                                                             
       Special-names .                                                               
           Decimal-point Is Comma .                                             
       Input-output Section .                                                   
       File-control.                                                            
           Select FFFFFGS Assign  FFFFFGS                                       
             Organization  Indexed                                              
             Access Mode  Dynamic                                               
             Record Key  FFFFFGS-CLE                                            
             File Status  W-FFFFFGS-STATUS  .                                   
       Data Division.                                                           
       File Section.                                                            
       Fd FFFFFGS                                                               
           Label Record  Standard                                               
           Data Record  FFFFFGS-ENREG.                                          
       Copy FFFFFFGS.                                                           
       FD SA-FICHIER                                                            
           Recording   V                                                        
           Record                                                               
           Varying                                                              
           From                                                                 
           1                                                                    
           To                                                                   
           4092                                                                 
           Depending                                                            
           On                                                                   
           W-SA-KEY                                                             
           Data Record  SA00                                                    
           Label Record  Standard                                               
           .                                                                    
       copy WSA000 replacing ==ZZZ== by ==CDE== ==XXX== by ==VAL==.             
       Working-storage Section.                                                 
       01 french1    pic x(100) value 'ça , ô Laetitia des îles !'.             
       01 french2    pic x(100) value 'à Pâques ou à Noël ? où ça ?'.           
       01 bytes.                                                                
         05 four-bytes pic x.                                                   
        03 fives-bytes pic x.                                                   
       01 full-word  Pic  s9(9)  Binary.                                        
       05 ptr4  Redefines full-word  Pointer.                                   
       01     L-QTE    PIC ZZ9V.99 BLANK WHEN ZERO.                             
       01 C Pic  Z(1)9.9 Value  Zero .                                          
       01 C Pic  Z(1)9.                                                         
       01 W Pic  S9(12)V999  Comp Value   -9,9.                                 
       01 7-3F PIC X.                                                           
       01 wfloat Comp-2 Value  +0.1E+01.                                        
007220******************************************************************70B003  
      * Déclare curseur                                                         
007240******************************************************************70B005  
007250     EXEC SQL                                                     COMP.DB2
007260       DECLARE C-MH37-U CURSOR   FOR                              COMP.DB2
007270       SELECT                                                     70B008  
007280            A.COETBL ,                                            70B011  
007420            A.COTNET                                              COMP.DB2
007430       FROM AFFVEAP   A                                           COMP.DB2
007440       WHERE                                                      COMP.DB2
007450 A.COETBL = :MH37-COETBL                                          COMP.DB2
007460 AND                                                              COMP.DB2
007470 A.COADHF = :MH37-COADHF                                          COMP.DB2
007480 AND                                                              COMP.DB2
007490 A.CETRTF = :MH37-CETRTF                                          COMP.DB2
007500 AND                                                              COMP.DB2
007510 A.COTRTO = :MH37-COTRTO                                          COMP.DB2
007520       FOR UPDATE OF                                              70B504  
007530          COTNET                                                  COMP.DB2
007540       OPTIMIZE FOR 1 ROWS                                        COMP.DB2
007550     END-EXEC.                                                    COMP.DB2
           01 PFKEY-INDICATOR  VALUE 00  PIC 99.                                
              88 ENTER-KEY VALUE 00.       88 CLEAR VALUE 93.                   
              88 PA1   VALUE 92. 88 PA2   VALUE 94. 88 PA3   VALUE 91.          
              88 PFK1  VALUE 1.  88 PFK2  VALUE 2.  88 PFK3  VALUE 3.           
       SKIP1                                                                    
       01  KONSTANTES.                                                          
           05  FILLER  PICTURE X(200)  VALUE                                    
                     '6337 XXXXX/02/09XXXXXXXXXXXX  16:28:15YYYYYYY FREE        
      -    '03/  /2005                                              wwww        
      -           '99999xxxxxxx ça éclate à être où < YYYYY000000GOOD'.         
                                                                                
                                                                                
       Linkage Section.                                                         
       01 ARBU009-parms.                                                        
       02 job-name  Pic  x(8).                                                  
       02 MSG-CLASS  Pic  x(8).                                                 
       02 ENV  Pic  x.                                                          
       88 BATCH Value  'b'.                                                     
       88 CICS Value  'c'.                                                      
       02 USER-ID  Pic  x(8).                                                   
       01 cb1.                                                                  
       05 ptr1   Pointer Occurs 256.                                            
       01 cb2.                                                                  
       05 ptr2   Pointer Occurs 256.                                            
      *                                                                         
      *--- ZONE POUR RETOUR DONNEES                        -----------*         
       Copy CXXXXX3C.                                                           
      **************************************************************            
       PROCEDURE DIVISION USING A                                               
                                                                                
                                B.                                              
      *************************************************                         
       Declaratives.                                                            
       SECEE  Section.                                                          
           Use  After  Error Procedure On EE-FICHIER                            
           .                                                                    
       F0AEE.                                                                   
           Move YSEE-STATUS To YA03-ZFILST                                      
           DISPLAY     'MANQUE PARAMETRE ''CCCCC='''                            
           .                                                                    
       F0A99.                                                                   
           Exit.                                                                
       End Declaratives.                                                        
       DANGLING-ELSE.                                                   00394818
           if cond1 greater or equal 1                                  00394819
             THEN DISPLAY 'COND1>='                                             
              if cond2 LESS THAN 10                                     00394819
                display 'cond2'                                                 
           else                                                         00394819
              display 'else cond1?'                                             
           else                                                                 
           Set Address Of cb1 To Null                                           
      D  Move  cb1(2:full-word)  To user-name .                                 
         if SUIVANT  then                                                       
         READ  FFFFFGS                                                          
         AT END IF COND THEN DISPLAY 'FIN'                                      
         DISPLAY 'FICHIER' END-IF                                               
         NOT AT END                                                             
         COMPUTE ERREUR = ERREUR * ERREUR                                       
         ON SIZE ERROR                                                          
                                                                                
         DISPLAY 'ERREUR'                                                       
         ELSE                                                                   
         DISPLAY 'STOP'.                                                        
                                                                                
                                                                                
                                                                                
         SKIP1                                                                  
       MAIN-PROCESS SECTION.                                                    
       MAIN-PROCESS-START.                                                      
               MOVE 'ATTENTION, LES FRAIS SONT A LA CHARGE DU DONNEUR D 00000000
      -             'ORDRE  : CONFIRMER.' TO TPO-ERRMSG1                00048960
                                                                                
               PERFORM Z-990-PROGRAM-ERROR.                                     
               MOVE All ' ' To Z                                                
               Move All 'ALL' To ALLZ.                                          
         SKIP1                                                                  
                   MOVE                                                         
                    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ZAPPZ        
      -    '03/02/2009                                                xy        
      -    '04/02/2009'                                                         
            TO Z                                                                
            .                                                                   
                                                                                
                                                                                
           STRING      'DOSSIER N  ' DELIMITED BY SIZE                          
           TB07-CODOSS DELIMITED BY SIZE                                        
           ' ' DELIMITED BY SIZE                                                
           TB07-CODOTR DELIMITED BY SIZE                                        
      -                                 ' : EVENEMENT DEJA EXISTANT DANS        
      -    ' TBCV (ZKOOV' DELIMITED BY SIZE                                     
      -                                 'A NOT = V), NE PEUT CREER UN NO        
      -    'UVEAU EVENEMENT ?????????????????????????' DELIMITED BY SIZE        
           'ENT' DELIMITED BY SIZE                                              
           INTO ERR-LIGNE                                                       
           .                                                                    
       MAIN-PROCESS-RETURN.                                                     
           EXIT.                                                                
       EJECT                                                                    
                                                                                
                                                                                
       U-100-READ-FQZ001E.                                                      
           EXEC CICS READ FILE(SEGNAME-FQZ001E)                                 
                              INTO(WT2625E)                                     
                              RIDFLD(E2625-CLE-PRIM-SAZT)                       
                              EQUAL                                             
                              KEYLENGTH(12)                                     
                              GENERIC                                           
                              NOHANDLE                                          
                              END-EXEC.                                         
794040 F81HF.                                                           P000    
794050     EXEC CICS   ASKTIME ABSTIME (YA2D-HEABS)          END-EXEC.  P100    
794060     EXEC CICS   FORMATTIME ABSTIME (YA2D-HEABS)                  P910    
794070                 DATESEP ('.') DDMMYY (YA2D-DABAM1)               P920    
794080                 TIME (YA2D-ZHETR) TIMESEP                        P930    
794090                 YEAR (YA2D-YEAR)                      END-EXEC.  P940    
794100     MOVE        YA2D-YEAR TO YA2D-ZDJSA.                         P950    
                                                                                
            .                                                                   
015600 F95-PQQ8-R.                                                      P002    
001000       exec sql                                                   12/10/22
      * une procédure stockée:                                                  
001100         call  ARBK005(:ARB-PGM-NAME)                             12/10/22
001200       end-exec                                                   12/10/22
001000       exec sql                                                   12/10/22
      * une autre procédure stockée:                                            
001100         call  myschema.ARBK006(:ARB-PGM-NAME)                    12/10/22
001200       end-exec                                                   12/10/22
001300       display '"exec sql call arbk005" sqlcode=' sqlcode         12/10/22
015610     MOVE        'QQ28' TO W-9T99-ZXEFF                           P004XXXX
015620     MOVE        'R' TO W-9T99-ZXEON                              P006XXXX
015630*ACCES TBXXECP                                                    P011XXXX
015640*  PGM xxxx83,xxxxx61.                                            P012XXXX
015650     EXEC SQL    SELECT                                           P032XXXX
015660            COUNT(*),                                             COMP.DB2
015660            A.LIIND1                                              COMP.DB2
015760                 INTO                                             P342XXXX
015770          :QQ28-LIIND1:V-QQ28-LIIND1                              COMP.DB2
azert *         :QQ28-LIIND1:V-QQ28-LIIND1                              COMP.DB2
015870                 FROM TBXXECP A                                   COMP.DB2
015880                 WHERE                                            COMP.DB2
015890                 A.COETBL = :QQ28-COETBL                          P661    
015900                 AND                                              P662    
015910                 A.COADHF = :QQ28-COADHF                          P663    
015920                 AND                                              P664    
015930                 A.COTRTO = :QQ28-COTRTO                          P665    
015940     END-EXEC.                                                    COMP.DB2
           EXEC SQL                                                             
          DECLARE C-TM00   CURSOR  WITH HOLD  FOR                               
          SELECT                                                                
            A.CTENRE ,                                                          
            A.COANAL ,                                                          
            A.COADHF                                                            
         FROM AFFVDKP   A , TABLE2 B                                            
         WHERE                                                                  
         (A.CTENRE = :TM00-CTENRE                                               
           AND                                                                  
           A.CTLGCO = :TM00-CTLGCO)  OR A.B  NOT IN ('e','r')                   
             AND (A BETWEEN 'e' AND 'f')                                        
             AND (A BETWEEN 1 and 2)                                            
          AND (A BETWEEN :X and :Y)                                             
             AND II NOT LIKE 'SZ44%'                                            
               AND YEAR(DFCHPA) = 10                                            
                                                                                
              GROUP BY A , B  HAVING (A > 0)                                    
                                                                                
             ORDER BY                                                           
              A.COADHF ,                                                        
            A.COSIR0 ,                                                          
              A.CTENRE DESC                                                     
                                                                                
              OPTIMIZE FOR 1 ROWS                                               
             FOR FETCH ONLY                                                     
             END-EXEC.                                                          
                                                                                
          EXEC SQL                                                              
        DECLARE C-TM00   CURSOR  WITH HOLD  FOR                                 
        SELECT                                                                  
            A.CTENRE ,                                                          
            A.MTLGC1 ,                                                          
            A.COANAL ,                                                          
            A.COADHF                                                            
        FROM BDEMAB    A   ,  AFFVDKP   B                                       
        WHERE                                                                   
          ((A.CTENRE = :TM00-CTENRE                                             
      *         AND                                                             
      *        A.CTLGCO = :TM00-CTLGCO                                          
              AND  NOT                                                          
             (A.COETAB < :WU76-COETAB)))                                        
             AND EXISTS                                                         
          (SELECT     B.CNRFLO FROM   TOTO)                                     
           AND (:FF00-DDVALT = (SELECT  B.CNRFLO FROM   TOTO))                  
               AND     A.ZTCREA >  CURRENT TIMESTAMP -  1 DAYS                  
                 GROUP BY A , B  HAVING COUNT(*) > 0                            
              OPTIMIZE FOR 1 ROWS                                               
                                                                                
           FETCH FIRST 999 ROWS ONLY                                            
              END-EXEC.                                                         
                                                                                
       U-100-SET-DA-STATUS-VSAM.                                                
           MOVE DA-STATUS-FILE TO ABT-VSAM-CICS-STATUS.                         
           IF DA-STATUS-FILE = DATASET-OK                                       
              MOVE DA-OK-LIT        TO DA-STATUS                                
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-NOTFND                                   
              MOVE DA-NOTFOUND-LIT  TO DA-STATUS                                
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-ENDFILE                                  
              MOVE DA-ENDFILE-LIT   TO DA-STATUS                                
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-DUPREC                                   
              MOVE DA-DUPREC-LIT TO DA-STATUS                                   
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-DUPKEY                                   
              MOVE DA-DUPKEY-LIT TO DA-STATUS                                   
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-DISABLED                                 
              MOVE DA-DISABLED-LIT TO DA-STATUS                                 
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-NOTAUTH                                  
              MOVE DA-NOTAUTH-LIT TO DA-STATUS                                  
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-ILLOGIC                                  
              MOVE DA-LOGICERR-LIT  TO DA-STATUS                                
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-INVREQ                                   
              MOVE DA-SECURITY-LIT  TO DA-STATUS                                
           ELSE                                                                 
           IF DA-STATUS-FILE = DATASET-NOTOPEN                                  
              MOVE DA-NOTAVAIL-LIT  TO DA-STATUS                                
           ELSE                                                                 
              MOVE DA-DBMERROR-LIT  TO DA-STATUS.                               
       SKIP1                                                                    
                                                                                
             EXEC DLI GU USING PCB(PCBNUM)                                      
             SEGMENT(SEGNAME)                                                   
              KEYS(CONKEYB) KEYLENGTH(8) SETPARENT                              
              SEGMENT(SEGC) INTO(AREAC) SEGLENGTH(SEGLEN)                       
              WHERE(KEYC=SEGKEYC) FIELDLENGTH(4) END-EXEC.                      
          PERFORM TEST-DIB THRU OK.                                             
                                                                                
                                                                                
                                                                                
       SKIP2                                                                    
       F92OQ-900.                                                               
            move 'PG000A' to ZL00-LCPG8                                         
          Exec Cics                                                             
             LINK PROGRAM (ZL00-LCPG8) COMMAREA (ZL99-LICOA) LENGTH             
             (ZL00-QLENR)                                                       
           End-exec                                                             
                                                                                
            move 'PG000B' to ZL00-LCPG8                                         
            Exec Cics                                                           
             LINK PROGRAM (ZL00-LCPG8) COMMAREA (ZL99-LICOA) LENGTH             
             (ZL00-QLENR)                                                       
           End-exec                                                             
                                                                                
      *************************************************************             
      * NOTE: ADDITIONAL PARAMETER ADDRESSES HAVE BEEN "PASSED"   *             
      *       TO ADLAATR  BY USE OF IT'S ENTRY POINTS ADLAAT0     *             
      *       ADLAAT1  AND ADLAAT2                                *             
      *************************************************************             
           CALL 'ADLAATR' USING DFHEIBLK                                        
                             DFHCOMMAREA                                        
                             TPO-ERRMSG1.                                       
                                                                                
           IF ABT-DO-WRITE                                                      
              MOVE ABT-ERROR-MESSAGE TO TPO-ERRMSG1                             
              PERFORM N-100-CURSOR-POSITION                                     
              MOVE DO-WRITE-LIT TO CONTROL-INDICATOR                            
              GO TO MAIN-PROCESS-RETURN                                         
           ELSE                                                                 
           IF ABT-DO-TRANSFER                                                   
              MOVE ABT-NEXT-PROGRAM-NAME TO NEXT-PROGRAM-NAME                   
              MOVE DO-TRANSFER-LIT TO CONTROL-INDICATOR                         
              GO TO MAIN-PROCESS-RETURN                                         
           else                                                                 
           IF ABT-CONTINUE-PROCESS                                              
              MOVE 'N' TO ABT-IN-PROGRESS                                       
           ELSE                                                                 
              EXEC CICS ABEND ABCODE('TABT') END-EXEC.                          
           IF W-FROMBIB = SPACES OR LOW-VALUE                                   
              IF W-VALLIG = 'OUI'                                               
                    IF W-VALIDE = 'O'                                           
                    MOVE 'N'              TO W-VALIDE                           
                 ELSE NEXT SENTENCE                                             
              ELSE NEXT SENTENCE                                                
           ELSE                                                                 
              IF W-FTYPBIB = SPACE                                              
                 MOVE SPACES          TO W-ISPF-VARLIST                         
              ELSE                                                              
                 MOVE RETURN-CODE  TO W-CODE-RETOUR                             
              END-IF                                                            
              IF NOT FONCTION-OK                                                
                 IF W-VALLIG = 'OUI'                                            
                    MOVE 'N'              TO W-VALIDE.                          
                                                                                
       Z-980-ABNORMAL-TERM-RETURN.                                              
           EXIT.                                                                
       EJECT                                                                    
                                                                                
       Z-700-COMPUTE-ALL.                                                       
                                                                                
664100     COMPUTE     RC00-MTRBA (J74JHR , J74JJR) =                   P110    
664200     RC00-MTRBA (J74JHR , J74JJR)                                 P120    
664300     * RC00-QPREVT                                                P130    
664400     / 100                                                        P140    
664500     COMPUTE     RT00-MTRBA (J74JHR , J74JJR) =                   P150    
664600     RT00-MTRBA (J74JHR , J74JJR)                                 P160    
664700     - RC00-MTRBA (J74JHR , J74JJR).                              P170    
995000*POUR FUSION, RESULTAT = PRESENTE                                 P150    
995100     COMPUTE     WK00-QTOBTQ = WK00-QTTIT                         P155    
995200     * (10                                                        P156    
995300     ** (WK00-CNDECV (1)                                          P157    
995400     - WK00-CTCLCQ)).                                             P158    
995500           IF    WT03-CTFCA = 'FO'                                P160    
995600           AND   J97QFR = WNVL                                    P161    
028800     COMPUTE     WK00-QTOBT9 = FUNCTION INTEGER                   P110
028900     (WK00-QTOBT9 + 0.01).                                        P111

