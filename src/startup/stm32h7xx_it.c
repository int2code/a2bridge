/**
 * @file stm32h7xx_it.c
 *
 * @copyright Copyright (c) 2026 int2code GmbH
 *
 */

#include "CoreIrq.h"

void HardFault_Handler(void)
{
    CoreIrq_Exception();
}

void NMI_Handler(void)
{
    HardFault_Handler();
}

void MemManage_Handler(void)
{
    HardFault_Handler();
}

void BusFault_Handler(void)
{
    HardFault_Handler();
}

void UsageFault_Handler(void)
{
    HardFault_Handler();
}

void DebugMon_Handler(void)
{
    HardFault_Handler();
}

void OTG_HS_IRQHandler(void)
{
    CoreIrq_OtgHs();
}

void TIM7_IRQHandler(void)
{
    CoreIrq_Tim7();
}

void EXTI15_10_IRQHandler(void)
{
    CoreIrq_Gpio14();
}

void EXTI9_5_IRQHandler(void)
{
    CoreIrq_Gpio5();
}

void DMA1_Stream0_IRQHandler(void)
{
    CoreIrq_DmaSai2B();
}

void DMA1_Stream1_IRQHandler(void)
{
    CoreIrq_DmaSai2A();
}

void DMA1_Stream2_IRQHandler(void)
{
    CoreIrq_DmaSai3B();
}

void DMA1_Stream3_IRQHandler(void)
{
    CoreIrq_DmaSai1A();
}

void DMA1_Stream4_IRQHandler(void)
{
    CoreIrq_DmaSai1B();
}

void DMA1_Stream5_IRQHandler(void)
{
    CoreIrq_DmaUart1();
}

void USART1_IRQHandler(void)
{
    CoreIrq_Uart1();
}

void SAI1_IRQHandler(void)
{
    CoreIrq_Sai1();
}

void SAI2_IRQHandler(void)
{
    CoreIrq_Sai2();
}

void SAI3_IRQHandler(void)
{
    CoreIrq_Sai3();
}
