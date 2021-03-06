from  scipy  import*
import numpy as np
import load_parameters
d=load_parameters.load_parameters()
locals().update(d)


def test_ode(x,t):
    
    p_gas_h2o = 0.0313*np.exp(5290*(1/T_base-1/T_op))  #0.0557 at 35°C
    K_w = (pow(10,(-14)))*np.exp((55900/(R*100))*(1/T_base-1/T_op))  # 2.08e-14
    K_a_va = pow(10,-4.86)
    K_a_bu = pow(10,-4.82)
    K_a_pro = pow(10,-4.88)
    K_a_ac =pow(10,-4.76)
    K_a_co2 = pow(10,(-6.35))*np.exp((7646/(R*100))*(1/T_base-1/T_op))  # 4.94e-7 at 35°C
    K_a_IN = pow(10,(-9.25))*np.exp((51965/(R*100))*(1/T_base-1/T_op))  # 1.11e-9 at 35°C
    K_H_co2 = 0.035*np.exp((-19410/(R*100))*(1/T_base-1/T_op)) #0.0271 at 35°C
    K_H_ch4 = 0.0014*np.exp((-14240/(R*100))*(1/T_base-1/T_op)) #0.00116 at 35°C
    K_H_h2 = 7.8e-4*np.exp((-4180/(R*100))*(1/T_base-1/T_op)) #7.38e-4 at 35°C
   
    u=np.array([0.1,0.1,0.1,0.1,0.1,0.1,0.1,0,0,0.0041256,0.17846,0.03,59.0229,0.1,0.1,0.1,0,0,0,0,0,0,0,34.2811,0.039126,0.178460,70,35])
    #------filter for negative value:
                   
    for i in range(42): 
        if (x[i] < 0):  
            x[i] = 0
        
    #---- pression----:
    
    p_gas_h2 = x[32]*R*T_op/16
    p_gas_ch4 = x[33]*R*T_op/64
    p_gas_co2 = x[34]*R*T_op
    P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o
    #---simplified gas flow calculation, Batstone 2002

    q_gas = k_P*(P_gas-P_atm) #.*P_gas/P_atm, 
    

     #---pH algebric calculation
    phi = x[24]+(x[10]-x[31])-x[30]-(x[29]/64)-(x[28]/112)-(x[27]/160)-(x[26]/208)-x[25]
    S_H_ion = (-1)*phi*0.5+0.5*np.sqrt(phi*phi+4*K_w)
    if S_H_ion<=0 :
        S_H_ion=pow(10,-12)

     
    pH_op = (-1)*np.log10(S_H_ion) # pH


    #---Hill function on SH+ => ulf version 2008

    pHLim_aa = pow(10,(-(pH_UL_aa + pH_LL_aa)/2))
    pHLim_ac = pow(10,(-(pH_UL_ac + pH_LL_ac)/2))
    pHLim_h2 = pow(10,(-(pH_UL_h2 + pH_LL_h2)/2))
    n_aa=3/(pH_UL_aa-pH_LL_aa)
    n_ac=3/(pH_UL_ac-pH_LL_ac)
    n_h2=3/(pH_UL_h2-pH_LL_h2)
    I_pH_aa = pow(pHLim_aa,n_aa)/(pow(S_H_ion,n_aa)+pow(pHLim_aa,n_aa))
    I_pH_ac = pow(pHLim_ac,n_ac)/(pow(S_H_ion,n_ac)+pow(pHLim_ac,n_ac))
    I_pH_h2 = pow(pHLim_h2,n_h2)/(pow(S_H_ion,n_h2)+pow(pHLim_h2,n_h2))
    
   
    #---Inhibition
    
    I_IN_lim = 1/(1+K_S_IN/x[10])
    I_h2_fa = 1/(1+x[7]/K_Ih2_fa)
    I_h2_c4 = 1/(1+x[7]/K_Ih2_c4)
    I_h2_pro = 1/(1+x[7]/K_Ih2_pro)
    I_nh3 = 1/(1+x[31]/K_I_nh3)
    
    inhib= zeros(6) 
    inhib[0] =(I_pH_aa*I_IN_lim) 
    inhib[1] = inhib[0]*I_h2_fa
    inhib[2] = inhib[0]*I_h2_c4
    inhib[3] = inhib[0]*I_h2_pro
    inhib[4] = I_pH_ac*I_IN_lim*I_nh3
    inhib[5] = I_pH_h2*I_IN_lim

    #---Biochemical Process rates
    
    proc1 = k_dis*x[12]
    proc2 = k_hyd_ch*x[13]
    proc3 = k_hyd_pr*x[14]
    proc4 = k_hyd_li*x[15]
    proc5 = (k_m_su*x[0]/(K_S_su+x[0]))*x[16]*inhib[0] 
    proc6 = (k_m_aa*x[1]/(K_S_aa+x[1]))*x[17]*inhib[0]
    proc7 = (k_m_fa*x[2]/(K_S_fa+x[2]))*x[18]*inhib[1]
    proc8 = (k_m_c4*x[3]/(K_S_c4+x[3]))*x[19]*(x[3]/(x[3]+x[4]+eps))*inhib[2]
    proc9 = (k_m_c4*x[4]/(K_S_c4+x[4]))*x[19]*(x[4]/(x[3]+x[4]+eps))*inhib[2]
    proc10 = (k_m_pro*x[5]/(K_S_pro+x[5]))*x[20]*inhib[3]
    proc11 = (k_m_ac*x[6]/(K_S_ac+x[6]))*x[21]*inhib[4]
    proc12 = (k_m_h2*x[7]/(K_S_h2+x[7]))*x[22]*inhib[5]
    proc13 = k_dec_Xsu*x[16]
    proc14 = k_dec_Xaa*x[17]
    proc15 =k_dec_Xfa*x[18]
    proc16 = k_dec_Xc4*x[19]
    proc17 = k_dec_Xpro*x[20]
    proc18 = k_dec_Xac*x[21]
    proc19 = k_dec_Xh2*x[22]
    

    #--- Acid-base rates
    
    procA4 = k_A_Bva*(x[26]*(K_a_va+S_H_ion)-K_a_va*x[3])
    procA5 = k_A_Bbu*(x[27]*(K_a_bu+S_H_ion)-K_a_bu*x[4])
    procA6 = k_A_Bpro*(x[28]*(K_a_pro+S_H_ion)-K_a_pro*x[5])
    procA7 = k_A_Bac*(x[29]*(K_a_ac+S_H_ion)-K_a_ac*x[6])
    procA10 = k_A_Bco2*(x[30]*(K_a_co2+S_H_ion)-K_a_co2*x[9])
    procA11 = k_A_BIN*(x[31]*(K_a_IN+S_H_ion)-K_a_IN*x[10])
    
    #--- Gas transfer rates
             
    procT8 = kLa*(x[7]-16*K_H_h2*p_gas_h2)
    procT9 = kLa*(x[8]-64*K_H_ch4*p_gas_ch4)
    procT10 = kLa*((x[9]-x[30])-K_H_co2*p_gas_co2)
    

    #--- reaction parameters

    stoich1 = -C_xc + f_sI_xc*C_sI + f_ch_xc*C_ch + f_pr_xc*C_pr + f_li_xc*C_li + f_xI_xc*C_xI
    stoich2 = -C_ch+C_su
    stoich3 = -C_pr+C_aa
    stoich4 = -C_li + (1-f_fa_li)*C_su + f_fa_li*C_fa
    stoich5 = -C_su + (1-Y_su)*(f_bu_su*C_bu+f_pro_su*C_pro+f_ac_su*C_ac) + Y_su*C_bac
    stoich6 = -C_aa + (1-Y_aa)*(f_va_aa*C_va+f_bu_aa*C_bu+f_pro_aa*C_pro+f_ac_aa*C_ac) + Y_aa*C_bac
    stoich7 = -C_fa + (1-Y_fa)*0.7*C_ac + Y_fa*C_bac
    stoich8 = -C_va + (1-Y_c4)*0.54*C_pro+(1-Y_c4)*0.31*C_ac+Y_c4*C_bac
    stoich9 = -C_bu + (1-Y_c4)*0.8*C_ac+Y_c4*C_bac
    stoich10 = -C_pro + (1-Y_pro)*0.57*C_ac+Y_pro*C_bac
    stoich11 = -C_ac + (1-Y_ac)*C_ch4+Y_ac*C_bac
    stoich12 = (1-Y_h2)*C_ch4 + Y_h2*C_bac
    stoich13 = -C_bac + C_xc

    reac1 = proc2+((1-f_fa_li)*proc4)-proc5
    reac2 = proc3-proc6
    reac3 = f_fa_li*proc4-proc7
    reac4 = (1-Y_aa)*f_va_aa*proc6-proc8
    reac5 = (1-Y_su)*f_bu_su*proc5+(1-Y_aa)*f_bu_aa*proc6-proc9
    reac6 = (1-Y_su)*f_pro_su*proc5+(1-Y_aa)*f_pro_aa*proc6+(1-Y_c4)*0.54*proc8-proc10
    reac7 = (1-Y_su)*f_ac_su*proc5+(1-Y_aa)*f_ac_aa*proc6+(1-Y_fa)*0.7*proc7+(1-Y_c4)*0.31*proc8+(1-Y_c4)*0.8*proc9+(1-Y_pro)*0.57*proc10-proc11
    reac8 = (1-Y_su)*f_h2_su*proc5+(1-Y_aa)*f_h2_aa*proc6+(1-Y_fa)*0.3*proc7+(1-Y_c4)*0.15*proc8+(1-Y_c4)*0.2*proc9+(1-Y_pro)*0.43*proc10-proc12-procT8
    reac9 = (1-Y_ac)*proc11+(1-Y_h2)*proc12-procT9
    reac10 = - stoich1*proc1 - stoich2*proc2 - stoich3*proc3 - stoich4*proc4 - stoich5*proc5 - stoich6*proc6 - stoich7*proc7 - stoich8*proc8 - stoich9*proc9 - stoich10*proc10 - stoich11*proc11 - stoich12*proc12 - stoich13*proc13 - stoich13*proc14 - stoich13*proc15 - stoich13*proc16 - stoich13*proc17 - stoich13*proc18 - stoich13*proc19 - procT10
    reac11 = (N_xc-f_xI_xc*N_I-f_sI_xc*N_I-f_pr_xc*N_aa)*proc1 - Y_su*N_bac*proc5 + (N_aa-Y_aa*N_bac)*proc6 - Y_fa*N_bac*proc7 - Y_c4*N_bac*proc8 - Y_c4*N_bac*proc9 - Y_pro*N_bac*proc10 - Y_ac*N_bac*proc11 - Y_h2*N_bac*proc12 + (N_bac-N_xc)*(proc13+proc14+proc15+proc16+proc17+proc18+proc19)
    reac12 = f_sI_xc*proc1
    reac13 = -proc1+proc13+proc14+proc15+proc16+proc17+proc18+proc19
    reac14 = f_ch_xc*proc1-proc2
    reac15 = f_pr_xc*proc1-proc3
    reac16 = f_li_xc*proc1-proc4
    reac17 = Y_su*proc5-proc13
    reac18 = Y_aa*proc6-proc14
    reac19 = Y_fa*proc7-proc15
    reac20 = Y_c4*proc8+Y_c4*proc9-proc16
    reac21 = Y_pro*proc10-proc17
    reac22 = Y_ac*proc11-proc18
    reac23 = Y_h2*proc12-proc19
    reac24 = f_xI_xc*proc1

    #---Gas flow calculation
    ####q_gas = R*T_op*V_liq*(procT8/16+procT9/64+procT10)/(P_atm-p_gas_h2o),

    if q_gas < 0 :
        q_gas = 0.0

    #---differential equation ///////////////////////////////////////////////
    dx=zeros(42)
    dx[0] = ((1/V_liq)*(u[26]*(u[0]-x[0])))+reac1  # Ssu
    dx[1] = 1/V_liq*(u[26]*(u[1]-x[1]))+reac2  # Saa
    dx[2] = 1/V_liq*(u[26]*(u[2]-x[2]))+reac3  # Sfa
    dx[3] = 1/V_liq*(u[26]*(u[3]-x[3]))+reac4  # Sva 
    dx[4] = 1/V_liq*(u[26]*(u[4]-x[4]))+reac5  # Sbu 
    dx[5] = 1/V_liq*(u[26]*(u[5]-x[5]))+reac6  # Spro 
    dx[6] = 1/V_liq*(u[26]*(u[6]-x[6]))+reac7  # Sac 
    dx[7] = 1/V_liq*(u[26]*(u[7]-x[7]))+reac8  # Sh2
    dx[8] = 1/V_liq*(u[26]*(u[8]-x[8]))+reac9  # Sch4
    dx[9] = 1/V_liq*(u[26]*(u[9]-x[9]))+reac10 # SIC
    dx[10] = 1/V_liq*(u[26]*(u[10]-x[10]))+reac11 # SIN 
    dx[11] = 1/V_liq*(u[26]*(u[11]-x[11]))+reac12 # SI
    dx[12] = 1/V_liq*(u[26]*(u[12]-x[12]))+reac13 # xc
    dx[13] = 1/V_liq*(u[26]*(u[13]-x[13]))+reac14 # Xch
    dx[14] = 1/V_liq*(u[26]*(u[14]-x[14]))+reac15 # Xpr
    dx[15] = 1/V_liq*(u[26]*(u[15]-x[15]))+reac16 # Xli
    dx[16] = 1/V_liq*(u[26]*(u[16]-x[16]))+reac17 # Xsu
    dx[17] = 1/V_liq*(u[26]*(u[17]-x[17]))+reac18 # Xaa
    dx[18] = 1/V_liq*(u[26]*(u[18]-x[18]))+reac19 # Xfa
    dx[19] = 1/V_liq*(u[26]*(u[19]-x[19]))+reac20 # Xc4
    dx[20] = 1/V_liq*(u[26]*(u[20]-x[20]))+reac21 # Xpr
    dx[21] = 1/V_liq*(u[26]*(u[21]-x[21]))+reac22 # Xac
    dx[22] = 1/V_liq*(u[26]*(u[22]-x[22]))+reac23 # Xh2
    dx[23] = 1/V_liq*(u[26]*(u[23]-x[23]))+reac24 # XI

    dx[24] = 1/V_liq*(u[26]*(u[24]-x[24])) # Scat+ 
    dx[25] = 1/V_liq*(u[26]*(u[25]-x[25])) # San- 

    dx[26] = -procA4  # Sva- 
    dx[27] = -procA5  # Sbu- 
    dx[28] = -procA6  # Spro- 
    dx[29] = -procA7  # Sac- 
    dx[30] = -procA10 # SHCO3- 
    dx[31] = -procA11 # SNH3 

    dx[32] = -x[32]*q_gas/V_gas+procT8*V_liq/V_gas #Sgas H2
    dx[33] = -x[33]*q_gas/V_gas+procT9*V_liq/V_gas #Sgas CH4
    dx[34] = -x[34]*q_gas/V_gas+procT10*V_liq/V_gas #Sgas CO2


   #---Dummy states*/

    dx[35] = 0
    dx[36] = 0 
    dx[37] = 0 
    dx[38] = 0
    dx[39] = 0
    dx[40] = 0
    dx[41] = 0
   
    
    return (dx)


