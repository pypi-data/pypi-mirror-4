C                                                                                      
C  L-BFGS-B IS RELEASED UNDER THE “NEW BSD LICENSE” (AKA “MODIFIED BSD LICENSE”        
C  OR “3-CLAUSE LICENSE”)                                                              
C  PLEASE READ ATTACHED FILE LICENSE.TXT                                               
C                                        
      SUBROUTINE TIMER(TTIME)
      DOUBLE PRECISION TTIME
C
      REAL TEMP
C
C     THIS ROUTINE COMPUTES CPU TIME IN DOUBLE PRECISION; IT MAKES USE OF 
C     THE INTRINSIC F90 CPU_TIME THEREFORE A CONVERSION TYPE IS
C     NEEDED.
C
C           J.L MORALES  DEPARTAMENTO DE MATEMATICAS, 
C                        INSTITUTO TECNOLOGICO AUTONOMO DE MEXICO
C                        MEXICO D.F.
C
C           J.L NOCEDAL  DEPARTMENT OF ELECTRICAL ENGINEERING AND
C                        COMPUTER SCIENCE.
C                        NORTHWESTERN UNIVERSITY. EVANSTON, IL. USA
C                         
C                        JANUARY 21, 2011
C
      TEMP = SNGL(TTIME)
      CALL CPU_TIME(TEMP)
      TTIME = DBLE(TEMP) 

      RETURN

      END
      
