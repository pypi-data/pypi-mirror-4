\* Source Pyomo model name=MASTER *\

min 
MASTER:
+1.000000 CVAR_COST_RootNode
 +0.0 ONE_VAR_CONSTANT

s.t.

c_e_BelowAverageScenario_PH_CVAR_BLOCK_CVAR_ETA_None_:
-1.000000 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 RootNode_CVAR_ETA
= 0.0

c_e_AverageScenario_PH_CVAR_BLOCK_CVAR_ETA_None_:
-1.000000 AverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 RootNode_CVAR_ETA
= 0.0

c_e_AboveAverageScenario_PH_CVAR_BLOCK_CVAR_ETA_None_:
-1.000000 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 RootNode_CVAR_ETA
= 0.0

c_e_BelowAverageScenario_DevotedAcreage_CORN_:
-1.000000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_AverageScenario_DevotedAcreage_CORN_:
-1.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_CORN_:
-1.000000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 RootNode_DevotedAcreage(CORN)
= 0.0

c_e_BelowAverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_AverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_SUGAR_BEETS_:
-1.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 RootNode_DevotedAcreage(SUGAR_BEETS)
= 0.0

c_e_BelowAverageScenario_DevotedAcreage_WHEAT_:
-1.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_AverageScenario_DevotedAcreage_WHEAT_:
-1.000000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_AboveAverageScenario_DevotedAcreage_WHEAT_:
-1.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 RootNode_DevotedAcreage(WHEAT)
= 0.0

c_e_BelowAverageScenario_RootNode_FirstStageCost_None_:
-1.000000 BelowAverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AverageScenario_RootNode_FirstStageCost_None_:
-1.000000 AverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AboveAverageScenario_RootNode_FirstStageCost_None_:
-1.000000 AboveAverageScenario_FirstStageCost
+1.000000 RootNode_FirstStageCost
= 0.0

c_e_AboveAverageScenario_AboveAverageNode_SecondStageCost_None_:
+1.000000 AboveAverageNode_SecondStageCost
-1.000000 AboveAverageScenario_SecondStageCost
= 0.0

c_e_BelowAverageScenario_BelowAverageNode_SecondStageCost_None_:
+1.000000 BelowAverageNode_SecondStageCost
-1.000000 BelowAverageScenario_SecondStageCost
= 0.0

c_e_AverageScenario_AverageNode_SecondStageCost_None_:
+1.000000 AverageNode_SecondStageCost
-1.000000 AverageScenario_SecondStageCost
= 0.0

c_e_COST_RootNode_FirstStageCost_None_:
-0.333333 EXPECTED_COST_AboveAverageNode
-0.333333 EXPECTED_COST_AverageNode
-0.333333 EXPECTED_COST_BelowAverageNode
+1.000000 EXPECTED_COST_RootNode
-1.000000 RootNode_FirstStageCost
= 0.0

c_e_COST_AboveAverageNode_SecondStageCost_None_:
-1.000000 AboveAverageNode_SecondStageCost
+1.000000 EXPECTED_COST_AboveAverageNode
= 0.0

c_e_COST_BelowAverageNode_SecondStageCost_None_:
-1.000000 BelowAverageNode_SecondStageCost
+1.000000 EXPECTED_COST_BelowAverageNode
= 0.0

c_e_COST_AverageNode_SecondStageCost_None_:
-1.000000 AverageNode_SecondStageCost
+1.000000 EXPECTED_COST_AverageNode
= 0.0

r_l_COMPUTE_CVAR_COST_:
-3.333333 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-3.333333 AverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-3.333333 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
+1.000000 CVAR_COST_RootNode
-1.000000 RootNode_CVAR_ETA
>= 0.0

r_u_COMPUTE_CVAR_COST_:
-3.333333 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-3.333333 AverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-3.333333 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
+1.000000 CVAR_COST_RootNode
-1.000000 RootNode_CVAR_ETA
<= 0.0

c_u_AverageScenario_ConstrainTotalAcreage_:
+1.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_AverageScenario_EnforceCattleFeedRequirement(CORN)_:
+3.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_QuantityPurchased(CORN)
-1.000000 AverageScenario_QuantitySubQuotaSold(CORN)
-1.000000 AverageScenario_QuantitySuperQuotaSold(CORN)
>= 240.0

c_l_AverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+20.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
-1.000000 AverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
>= 0.0

c_l_AverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+2.500000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_QuantityPurchased(WHEAT)
-1.000000 AverageScenario_QuantitySubQuotaSold(WHEAT)
-1.000000 AverageScenario_QuantitySuperQuotaSold(WHEAT)
>= 200.0

c_u_AverageScenario_LimitAmountSold(CORN)_:
-3.000000 AverageScenario_DevotedAcreage(CORN)
+1.000000 AverageScenario_QuantitySubQuotaSold(CORN)
+1.000000 AverageScenario_QuantitySuperQuotaSold(CORN)
<= 0.0

c_u_AverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-20.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+1.000000 AverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
<= 0.0

c_u_AverageScenario_LimitAmountSold(WHEAT)_:
-2.500000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_QuantitySubQuotaSold(WHEAT)
+1.000000 AverageScenario_QuantitySuperQuotaSold(WHEAT)
<= 0.0

r_l_AverageScenario_EnforceQuotas(CORN)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(CORN)
>= 0.0

r_u_AverageScenario_EnforceQuotas(CORN)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(CORN)
<= 100000.0

r_l_AverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
>= 0.0

r_u_AverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
<= 6000.0

r_l_AverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(WHEAT)
>= 0.0

r_u_AverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 AverageScenario_QuantitySubQuotaSold(WHEAT)
<= 100000.0

c_e_AverageScenario_ComputeFirstStageCost_:
-230.000000 AverageScenario_DevotedAcreage(CORN)
-260.000000 AverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 AverageScenario_DevotedAcreage(WHEAT)
+1.000000 AverageScenario_FirstStageCost
= 0.0

c_e_AverageScenario_ComputeSecondStageCost_:
-210.000000 AverageScenario_QuantityPurchased(CORN)
-100000.000000 AverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 AverageScenario_QuantityPurchased(WHEAT)
+150.000000 AverageScenario_QuantitySubQuotaSold(CORN)
+36.000000 AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+170.000000 AverageScenario_QuantitySubQuotaSold(WHEAT)
+10.000000 AverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
+1.000000 AverageScenario_SecondStageCost
= 0.0

r_l_AverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 AverageScenario_FirstStageCost
+1.000000 AverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 AverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 AverageScenario_SecondStageCost
>= 0.0

r_u_AverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 AverageScenario_FirstStageCost
+1.000000 AverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 AverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 AverageScenario_SecondStageCost
<= 0.0

c_u_BelowAverageScenario_ConstrainTotalAcreage_:
+1.000000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(CORN)_:
+2.400000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_QuantityPurchased(CORN)
-1.000000 BelowAverageScenario_QuantitySubQuotaSold(CORN)
-1.000000 BelowAverageScenario_QuantitySuperQuotaSold(CORN)
>= 240.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+16.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
-1.000000 BelowAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
>= 0.0

c_l_BelowAverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+2.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_QuantityPurchased(WHEAT)
-1.000000 BelowAverageScenario_QuantitySubQuotaSold(WHEAT)
-1.000000 BelowAverageScenario_QuantitySuperQuotaSold(WHEAT)
>= 200.0

c_u_BelowAverageScenario_LimitAmountSold(CORN)_:
-2.400000 BelowAverageScenario_DevotedAcreage(CORN)
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(CORN)
+1.000000 BelowAverageScenario_QuantitySuperQuotaSold(CORN)
<= 0.0

c_u_BelowAverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-16.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+1.000000 BelowAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
<= 0.0

c_u_BelowAverageScenario_LimitAmountSold(WHEAT)_:
-2.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(WHEAT)
+1.000000 BelowAverageScenario_QuantitySuperQuotaSold(WHEAT)
<= 0.0

r_l_BelowAverageScenario_EnforceQuotas(CORN)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(CORN)
>= 0.0

r_u_BelowAverageScenario_EnforceQuotas(CORN)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(CORN)
<= 100000.0

r_l_BelowAverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
>= 0.0

r_u_BelowAverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
<= 6000.0

r_l_BelowAverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(WHEAT)
>= 0.0

r_u_BelowAverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 BelowAverageScenario_QuantitySubQuotaSold(WHEAT)
<= 100000.0

c_e_BelowAverageScenario_ComputeFirstStageCost_:
-230.000000 BelowAverageScenario_DevotedAcreage(CORN)
-260.000000 BelowAverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 BelowAverageScenario_DevotedAcreage(WHEAT)
+1.000000 BelowAverageScenario_FirstStageCost
= 0.0

c_e_BelowAverageScenario_ComputeSecondStageCost_:
-210.000000 BelowAverageScenario_QuantityPurchased(CORN)
-100000.000000 BelowAverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 BelowAverageScenario_QuantityPurchased(WHEAT)
+150.000000 BelowAverageScenario_QuantitySubQuotaSold(CORN)
+36.000000 BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+170.000000 BelowAverageScenario_QuantitySubQuotaSold(WHEAT)
+10.000000 BelowAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
+1.000000 BelowAverageScenario_SecondStageCost
= 0.0

r_l_BelowAverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 BelowAverageScenario_FirstStageCost
+1.000000 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 BelowAverageScenario_SecondStageCost
>= 0.0

r_u_BelowAverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 BelowAverageScenario_FirstStageCost
+1.000000 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 BelowAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 BelowAverageScenario_SecondStageCost
<= 0.0

c_u_AboveAverageScenario_ConstrainTotalAcreage_:
+1.000000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
<= 500.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(CORN)_:
+3.600000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_QuantityPurchased(CORN)
-1.000000 AboveAverageScenario_QuantitySubQuotaSold(CORN)
-1.000000 AboveAverageScenario_QuantitySuperQuotaSold(CORN)
>= 240.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(SUGAR_BEETS)_:
+24.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_QuantityPurchased(SUGAR_BEETS)
-1.000000 AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
-1.000000 AboveAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
>= 0.0

c_l_AboveAverageScenario_EnforceCattleFeedRequirement(WHEAT)_:
+3.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_QuantityPurchased(WHEAT)
-1.000000 AboveAverageScenario_QuantitySubQuotaSold(WHEAT)
-1.000000 AboveAverageScenario_QuantitySuperQuotaSold(WHEAT)
>= 200.0

c_u_AboveAverageScenario_LimitAmountSold(CORN)_:
-3.600000 AboveAverageScenario_DevotedAcreage(CORN)
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(CORN)
+1.000000 AboveAverageScenario_QuantitySuperQuotaSold(CORN)
<= 0.0

c_u_AboveAverageScenario_LimitAmountSold(SUGAR_BEETS)_:
-24.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+1.000000 AboveAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
<= 0.0

c_u_AboveAverageScenario_LimitAmountSold(WHEAT)_:
-3.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(WHEAT)
+1.000000 AboveAverageScenario_QuantitySuperQuotaSold(WHEAT)
<= 0.0

r_l_AboveAverageScenario_EnforceQuotas(CORN)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(CORN)
>= 0.0

r_u_AboveAverageScenario_EnforceQuotas(CORN)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(CORN)
<= 100000.0

r_l_AboveAverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
>= 0.0

r_u_AboveAverageScenario_EnforceQuotas(SUGAR_BEETS)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
<= 6000.0

r_l_AboveAverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(WHEAT)
>= 0.0

r_u_AboveAverageScenario_EnforceQuotas(WHEAT)_:
+1.000000 AboveAverageScenario_QuantitySubQuotaSold(WHEAT)
<= 100000.0

c_e_AboveAverageScenario_ComputeFirstStageCost_:
-230.000000 AboveAverageScenario_DevotedAcreage(CORN)
-260.000000 AboveAverageScenario_DevotedAcreage(SUGAR_BEETS)
-150.000000 AboveAverageScenario_DevotedAcreage(WHEAT)
+1.000000 AboveAverageScenario_FirstStageCost
= 0.0

c_e_AboveAverageScenario_ComputeSecondStageCost_:
-210.000000 AboveAverageScenario_QuantityPurchased(CORN)
-100000.000000 AboveAverageScenario_QuantityPurchased(SUGAR_BEETS)
-238.000000 AboveAverageScenario_QuantityPurchased(WHEAT)
+150.000000 AboveAverageScenario_QuantitySubQuotaSold(CORN)
+36.000000 AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS)
+170.000000 AboveAverageScenario_QuantitySubQuotaSold(WHEAT)
+10.000000 AboveAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS)
+1.000000 AboveAverageScenario_SecondStageCost
= 0.0

r_l_AboveAverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 AboveAverageScenario_FirstStageCost
+1.000000 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 AboveAverageScenario_SecondStageCost
>= 0.0

r_u_AboveAverageScenario_PH_CVAR_BLOCK_COMPUTE_SCENARIO_EXCESS_:
-1.000000 AboveAverageScenario_FirstStageCost
+1.000000 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_ETA
+1.000000 AboveAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS
-1.000000 AboveAverageScenario_SecondStageCost
<= 0.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    -inf <= RootNode_CVAR_ETA <= +inf
    -inf <= RootNode_DevotedAcreage(CORN) <= +inf
    -inf <= RootNode_DevotedAcreage(SUGAR_BEETS) <= +inf
    -inf <= RootNode_DevotedAcreage(WHEAT) <= +inf
    -inf <= EXPECTED_COST_RootNode <= +inf
    -inf <= EXPECTED_COST_AboveAverageNode <= +inf
    -inf <= EXPECTED_COST_BelowAverageNode <= +inf
    -inf <= EXPECTED_COST_AverageNode <= +inf
    -inf <= CVAR_COST_RootNode <= +inf
    -inf <= RootNode_FirstStageCost <= +inf
    -inf <= AboveAverageNode_SecondStageCost <= +inf
    -inf <= BelowAverageNode_SecondStageCost <= +inf
    -inf <= AverageNode_SecondStageCost <= +inf
   0.0 <= AverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= AverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= AverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= AverageScenario_QuantitySubQuotaSold(CORN) <= +inf
   0.0 <= AverageScenario_QuantitySubQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= AverageScenario_QuantitySubQuotaSold(WHEAT) <= +inf
   0.0 <= AverageScenario_QuantitySuperQuotaSold(CORN) <= +inf
   0.0 <= AverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= AverageScenario_QuantitySuperQuotaSold(WHEAT) <= +inf
   0.0 <= AverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= AverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= AverageScenario_QuantityPurchased(WHEAT) <= +inf
    -inf <= AverageScenario_FirstStageCost <= +inf
    -inf <= AverageScenario_SecondStageCost <= +inf
   0 <= AverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS <= +inf
    -inf <= AverageScenario_PH_CVAR_BLOCK_CVAR_ETA <= +inf
   0.0 <= BelowAverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= BelowAverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= BelowAverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= BelowAverageScenario_QuantitySubQuotaSold(CORN) <= +inf
   0.0 <= BelowAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= BelowAverageScenario_QuantitySubQuotaSold(WHEAT) <= +inf
   0.0 <= BelowAverageScenario_QuantitySuperQuotaSold(CORN) <= +inf
   0.0 <= BelowAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= BelowAverageScenario_QuantitySuperQuotaSold(WHEAT) <= +inf
   0.0 <= BelowAverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= BelowAverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= BelowAverageScenario_QuantityPurchased(WHEAT) <= +inf
    -inf <= BelowAverageScenario_FirstStageCost <= +inf
    -inf <= BelowAverageScenario_SecondStageCost <= +inf
   0 <= BelowAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS <= +inf
    -inf <= BelowAverageScenario_PH_CVAR_BLOCK_CVAR_ETA <= +inf
   0.0 <= AboveAverageScenario_DevotedAcreage(CORN) <= 500
   0.0 <= AboveAverageScenario_DevotedAcreage(SUGAR_BEETS) <= 500
   0.0 <= AboveAverageScenario_DevotedAcreage(WHEAT) <= 500
   0.0 <= AboveAverageScenario_QuantitySubQuotaSold(CORN) <= +inf
   0.0 <= AboveAverageScenario_QuantitySubQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= AboveAverageScenario_QuantitySubQuotaSold(WHEAT) <= +inf
   0.0 <= AboveAverageScenario_QuantitySuperQuotaSold(CORN) <= +inf
   0.0 <= AboveAverageScenario_QuantitySuperQuotaSold(SUGAR_BEETS) <= +inf
   0.0 <= AboveAverageScenario_QuantitySuperQuotaSold(WHEAT) <= +inf
   0.0 <= AboveAverageScenario_QuantityPurchased(CORN) <= +inf
   0.0 <= AboveAverageScenario_QuantityPurchased(SUGAR_BEETS) <= +inf
   0.0 <= AboveAverageScenario_QuantityPurchased(WHEAT) <= +inf
    -inf <= AboveAverageScenario_FirstStageCost <= +inf
    -inf <= AboveAverageScenario_SecondStageCost <= +inf
   0 <= AboveAverageScenario_PH_CVAR_BLOCK_CVAR_EXCESS <= +inf
    -inf <= AboveAverageScenario_PH_CVAR_BLOCK_CVAR_ETA <= +inf
end 
